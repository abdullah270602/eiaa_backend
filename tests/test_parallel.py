import os
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from config import *

class PathResolver:
    """Handles intelligent path resolution for test files"""
    
    @staticmethod
    def find_test_directory(directory: str = DEFAULT_TEST_DIR) -> Optional[str]:
        """Find the test directory using intelligent path resolution"""
        
        # If absolute path provided, use it directly
        if os.path.isabs(directory):
            return directory if os.path.exists(directory) else None
        
        # Try current directory first
        if os.path.exists(directory):
            return os.path.abspath(directory)
        
        # Try predefined possible locations
        for possible_path in POSSIBLE_TEST_DIRS:
            test_path = possible_path.replace("test_files", directory)
            if os.path.exists(test_path):
                return os.path.abspath(test_path)
        
        return None
    
    @staticmethod
    def discover_test_files(directory: str) -> List[str]:
        """Discover all test files in the given directory"""
        test_files = []
        resolved_dir = PathResolver.find_test_directory(directory)
        
        if not resolved_dir:
            return test_files
        
        for file_name in sorted(os.listdir(resolved_dir)):
            if file_name.endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(resolved_dir, file_name)
                test_files.append(file_path)
        
        return test_files

class TemplateDetector:
    """Handles template type detection from file names"""
    
    @staticmethod
    def detect_template_from_filename(file_name: str) -> Optional[str]:
        """Detect template type from filename using keyword matching"""
        file_name_lower = file_name.lower()
        
        for template_type, keywords in TEMPLATE_KEYWORDS.items():
            if any(keyword in file_name_lower for keyword in keywords):
                return template_type
        
        return None
    
    @staticmethod
    def get_forced_templates(test_files: List[str]) -> Dict[str, str]:
        """Get files that should be tested with forced templates (only complete files)"""
        force_templates = {}
        
        for file_path in test_files:
            file_name = os.path.basename(file_path)
            
            # Only add forced template for "complete" files to avoid redundancy
            if "complete" in file_name.lower():
                template_type = TemplateDetector.detect_template_from_filename(file_name)
                if template_type:
                    force_templates[file_name] = template_type
        
        return force_templates

class AsyncTestRunner:
    """Handles parallel test execution with batching"""
    
    def __init__(self, base_url: str = BASE_URL, max_concurrent: int = MAX_CONCURRENT_REQUESTS):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent * 2)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_single_file(self, file_path: str, test_mode: str, force_template: Optional[str] = None) -> Dict[str, Any]:
        """Test a single file with rate limiting"""
        async with self.semaphore:
            return await self._execute_test(file_path, test_mode, force_template)
    
    async def _execute_test(self, file_path: str, test_mode: str, force_template: Optional[str] = None) -> Dict[str, Any]:
        """Execute the actual test request"""
        file_name = os.path.basename(file_path)
        
        try:
            # Prepare request parameters
            url = f"{self.base_url}{UPLOAD_ENDPOINT}"
            params = {}
            
            if test_mode == "FORCED" and force_template:
                params['force_template'] = force_template
            
            # Check if file exists before trying to read it
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Test file not found: {file_path}")
            
            # Read file and prepare form data
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            if not file_content:
                raise ValueError(f"File is empty: {file_path}")
            
            data = aiohttp.FormData()
            content_type = 'text/csv' if file_name.endswith('.csv') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            data.add_field('file', file_content, filename=file_name, content_type=content_type)
            
            # Execute request
            start_time = time.time()
            async with self.session.post(url, data=data, params=params) as response:
                end_time = time.time()
                processing_time = round(end_time - start_time, 2)
                
                # Debug logging
                print(f"    🔍 {file_name} | {test_mode} | Status: {response.status} | Time: {processing_time}s")
                
                # Parse response
                result = await self._parse_response(response, file_path, test_mode, force_template, processing_time)
                
                # Log result
                status_icon = "✅" if result["success"] else "❌"
                template = result.get('detected_template', 'N/A')
                confidence = result.get('detection_confidence', 0)
                print(f"  {status_icon} {file_name} | {test_mode} | {processing_time}s | {template} ({confidence:.2f})")
                
                return result
                
        except asyncio.TimeoutError:
            error_msg = f"Request timed out after {REQUEST_TIMEOUT} seconds"
            print(f"  ⏰ TIMEOUT in {file_name} | {test_mode}: {error_msg}")
            return self._create_error_result(file_path, test_mode, force_template, error_msg)
        except aiohttp.ClientError as e:
            error_msg = f"Client error: {str(e)}"
            print(f"  🔌 CLIENT ERROR in {file_name} | {test_mode}: {error_msg}")
            return self._create_error_result(file_path, test_mode, force_template, error_msg)
        except Exception as e:
            error_msg = str(e) if str(e) else f"Unknown error: {type(e).__name__}"
            print(f"  ❌ ERROR in {file_name} | {test_mode}: {error_msg}")
            return self._create_error_result(file_path, test_mode, force_template, error_msg)
    
    async def _parse_response(self, response, file_path: str, test_mode: str, force_template: Optional[str], processing_time: float) -> Dict[str, Any]:
        """Parse HTTP response and extract metadata"""
        file_name = os.path.basename(file_path)
        
        result = {
            "file_name": file_name,
            "file_path": file_path,
            "test_mode": test_mode,
            "force_template": force_template,
            "test_timestamp": datetime.now().isoformat(),
            "status_code": response.status,
            "processing_time_seconds": processing_time,
            "success": response.status == 200,
            "response_size_bytes": int(response.headers.get('content-length', 0)),
            "response_content_type": response.headers.get('content-type', 'unknown')
        }
        
        # Parse metadata from headers
        if response.status == 200:
            metadata_header = response.headers.get('X-Processing-Result')
            print(f"    🔍 Metadata header present: {metadata_header is not None}")
            if metadata_header:
                try:
                    metadata = json.loads(metadata_header)
                    print(f"    ✅ Metadata parsed successfully")
                    
                    # Extract template detection info
                    if "template_detection" in metadata:
                        result["detected_template"] = metadata.get("template_type", "unknown")
                        result["detection_confidence"] = metadata["template_detection"].get("confidence", 0)
                        result["detection_method"] = metadata["template_detection"].get("method", "unknown")
                    
                    # Extract mapping info
                    if "column_mapping" in metadata:
                        mapping_info = metadata["column_mapping"]
                        result["columns_mapped"] = len(mapping_info.get("column_mapping", {}))
                        result["unmatched_columns"] = mapping_info.get("unmatched_columns", [])
                        result["missing_required"] = mapping_info.get("missing_required", [])
                    
                    result["metadata"] = metadata
                    
                except json.JSONDecodeError as e:
                    print(f"    ❌ JSON decode error: {e}")
                    result["metadata_error"] = f"Failed to parse metadata: {str(e)}"
            else:
                print(f"    ⚠️ No X-Processing-Result header found")
        else:
            error_content = await response.text()
            result["error_message"] = error_content[:500]  # Limit error message length
            print(f"    ❌ Non-200 status: {response.status}, Error: {error_content[:100]}")
        
        return result
    
    def _create_error_result(self, file_path: str, test_mode: str, force_template: Optional[str], error_message: str) -> Dict[str, Any]:
        """Create error result object"""
        return {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "test_mode": test_mode,
            "force_template": force_template,
            "test_timestamp": datetime.now().isoformat(),
            "status_code": None,
            "processing_time_seconds": None,
            "success": False,
            "error_message": error_message,
            "error_type": "RequestException"
        }
    
    async def run_parallel_tests(self, test_tasks: List[Tuple[str, str, Optional[str]]]) -> List[Dict[str, Any]]:
        """Run multiple tests in parallel with batching"""
        print(f"🚀 Running {len(test_tasks)} tests with max {self.max_concurrent} concurrent requests...")
        
        # Create coroutines for all tests
        coroutines = [
            self.test_single_file(file_path, test_mode, force_template)
            for file_path, test_mode, force_template in test_tasks
        ]
        
        # Execute all tests concurrently and wait for completion
        print(f"⏳ Waiting for all {len(coroutines)} tests to complete...")
        print(f"🔗 Session status: {'Active' if self.session and not self.session.closed else 'Inactive'}")
        
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Handle any exceptions and provide detailed logging
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                file_path, test_mode, force_template = test_tasks[i]
                print(f"  ❌ Exception for {os.path.basename(file_path)} | {test_mode}: {result}")
                processed_results.append(
                    self._create_error_result(file_path, test_mode, force_template, str(result))
                )
            else:
                processed_results.append(result)
        
        return processed_results

class TemplateSystemTester:
    """Main tester class with parallel execution capabilities"""
    
    def __init__(self, base_url: str = BASE_URL, max_concurrent: int = MAX_CONCURRENT_REQUESTS):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.test_results = []
        self.start_time = datetime.now()
    
    def prepare_test_tasks(self, test_files: List[str], force_templates: Dict[str, str]) -> List[Tuple[str, str, Optional[str]]]:
        """Prepare all test tasks to be executed"""
        tasks = []
        
        for file_path in test_files:
            file_name = os.path.basename(file_path)
            
            # Task 1: Standard auto-detection
            tasks.append((file_path, "STANDARD", None))
            
            # Task 2: Forced template (if applicable)
            if file_name in force_templates:
                tasks.append((file_path, "FORCED", force_templates[file_name]))
        
        return tasks
    
    async def run_comprehensive_test(self, test_directory: str) -> None:
        """Run comprehensive test suite"""
        # Check server connectivity first
        print(f"🔌 Checking server connectivity at {self.base_url}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/docs") as response:
                    if response.status == 200:
                        print(f"✅ Server is running and accessible")
                    else:
                        print(f"⚠️ Server responded with status {response.status}")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print(f"💡 Make sure the server is running at {self.base_url}")
            return
        
        # Discover test files
        test_files = PathResolver.discover_test_files(test_directory)
        
        if not test_files:
            print(f"❌ No test files found in directory: {test_directory}")
            return
        
        print(f"📋 Discovered {len(test_files)} test files:")
        for file_path in test_files:
            print(f"  • {os.path.basename(file_path)}")
        
        # Detect forced templates
        force_templates = TemplateDetector.get_forced_templates(test_files)
        
        print(f"\n🎛️ Files with forced template testing: {len(force_templates)}")
        for file, template in force_templates.items():
            print(f"  {file} → {template}")
        
        # Prepare test tasks
        test_tasks = self.prepare_test_tasks(test_files, force_templates)
        
        print(f"\n📊 Total test tasks: {len(test_tasks)}")
        print(f"🔄 Max concurrent requests: {self.max_concurrent}")
        print()
        
        # Execute tests
        async with AsyncTestRunner(self.base_url, self.max_concurrent) as runner:
            self.test_results = await runner.run_parallel_tests(test_tasks)
        
        print(f"\n✅ All tests completed!")
    
    def generate_report(self, output_dir: str = REPORT_OUTPUT_DIR):
        """Generate test reports (same as before but uses constants)"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Generate reports
        json_file = os.path.join(output_dir, f"test_results_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        csv_file = os.path.join(output_dir, f"test_summary_{timestamp}.csv")
        df = pd.DataFrame(self.test_results)
        df.to_csv(csv_file, index=False)
        
        self._print_summary()
        
        print(f"\n📁 Test results saved to:")
        print(f"  📄 JSON: {json_file}")
        print(f"  📊 CSV: {csv_file}")
    
    def _print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        print(f"\n" + "="*60)
        print(f"📊 TEST SUMMARY")
        print(f"="*60)
        print(f"🎯 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📁 Files Tested: {len(set(r['file_name'] for r in self.test_results))}")
        print(f"⏱️ Total Time: {sum(r.get('processing_time_seconds', 0) for r in self.test_results if r.get('processing_time_seconds')):.1f}s")
        print(f"🔄 Concurrency: {self.max_concurrent} parallel requests")
        
        # Test mode breakdown
        print(f"\n📋 TEST MODE BREAKDOWN:")
        mode_stats = {}
        for result in self.test_results:
            mode = result.get('test_mode', 'unknown')
            if mode not in mode_stats:
                mode_stats[mode] = {'total': 0, 'success': 0}
            mode_stats[mode]['total'] += 1
            if result.get('success'):
                mode_stats[mode]['success'] += 1
        
        for mode, stats in mode_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"  {mode}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Template detection accuracy
        print(f"\n🎯 TEMPLATE DETECTION ACCURACY:")
        template_stats = {}
        for result in self.test_results:
            if result.get('success') and result.get('detected_template'):
                template = result['detected_template']
                confidence = result.get('detection_confidence', 0)
                if template not in template_stats:
                    template_stats[template] = []
                template_stats[template].append(confidence)
        
        for template, confidences in template_stats.items():
            avg_confidence = sum(confidences) / len(confidences)
            high_conf_count = sum(1 for c in confidences if c >= CONFIDENCE_THRESHOLDS['HIGH'])
            print(f"  {template}: {high_conf_count}/{len(confidences)} high confidence (avg: {avg_confidence:.2f})")

async def main():
    import sys
    
    # Get test directory from command line or use default
    test_directory = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_DIR
    
    # Get max concurrent requests from command line (optional)
    max_concurrent = MAX_CONCURRENT_REQUESTS
    if len(sys.argv) > 2:
        try:
            max_concurrent = int(sys.argv[2])
            max_concurrent = max(1, min(max_concurrent, 20))  # Limit between 1-20
        except ValueError:
            print(f"⚠️ Invalid concurrency value, using default: {MAX_CONCURRENT_REQUESTS}")
    
    print(f"📁 Test directory: {test_directory}")
    print(f"🔄 Max concurrent requests: {max_concurrent}")
    print(f"🌐 Server URL: {BASE_URL}")
    print()
    
    # Initialize and run tester
    tester = TemplateSystemTester(BASE_URL, max_concurrent)
    await tester.run_comprehensive_test(test_directory)
    tester.generate_report()

if __name__ == "__main__":
    import sys
    
    print("🚀 Template System Parallel Testing Tool")
    print("=" * 50)
    print("💡 Usage: python test_parallel.py [test_directory] [max_concurrent_requests]")
    print("💡 Example: python test_parallel.py test_files 8")
    print()
    
    asyncio.run(main())
