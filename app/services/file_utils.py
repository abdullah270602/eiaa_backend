import re
import pandas as pd
from typing import Tuple, Dict, List, Union
from io import BytesIO

def extract_preview_data(file: BytesIO, extension: str) -> Tuple[Dict[str, List[str]], pd.DataFrame]:
    """Reads file and returns a sample of the first 10 values for each column, and full df"""
    try:
        if extension == ".csv":
            # Try reading with various fallback options for malformed CSV files
            try:
                # First attempt - standard reading
                df = pd.read_csv(file)
            except pd.errors.ParserError as e:
                print(f"ParserError encountered: {e}")
                # Reset file pointer for retry
                file.seek(0)
                try:
                    # Try with skip bad lines (modern pandas)
                    df = pd.read_csv(file, on_bad_lines='skip')
                    print(f"Successfully read with on_bad_lines='skip', shape: {df.shape}")
                except (TypeError, AttributeError):
                    # Fallback for older pandas versions
                    file.seek(0)
                    try:
                        df = pd.read_csv(file, error_bad_lines=False, warn_bad_lines=True)
                        print(f"Successfully read with error_bad_lines=False, shape: {df.shape}")
                    except:
                        # Last resort - use python engine with more flexible parsing
                        file.seek(0)
                        df = pd.read_csv(file, engine='python', sep=',', quoting=1, 
                                       skipinitialspace=True, on_bad_lines='skip')
                        print(f"Successfully read with python engine, shape: {df.shape}")
            except Exception as e:
                # Final fallback - try to read as text and clean
                file.seek(0)
                print(f"All CSV reading methods failed: {e}")
                try:
                    # Read raw text and try to clean it
                    content = file.read().decode('utf-8', errors='ignore')
                    # Simple cleaning - remove line breaks within quoted fields
                    import io
                    cleaned_content = content.replace('\n', ' ').replace('\r', '')
                    df = pd.read_csv(io.StringIO(cleaned_content), engine='python', on_bad_lines='skip')
                    print(f"Successfully read after text cleaning, shape: {df.shape}")
                except Exception as final_e:
                    raise ValueError(f"Could not parse CSV file even with all fallback methods: {final_e}")
        else:
            df = pd.read_excel(file)

        # Ensure we have some data
        if df.empty:
            raise ValueError("The file appears to be empty after processing")

        # Clean column names (remove any newlines or extra spaces)
        df.columns = [str(col).strip().replace('\n', ' ').replace('\r', '') for col in df.columns]
        
        preview_data = {
            col: df[col].dropna().astype(str).head(10).tolist()
            for col in df.columns
        }
        return preview_data, df
    except pd.errors.EmptyDataError:
        raise ValueError("The file appears to be empty")
    except Exception as e:
        import traceback; traceback.print_exc();
        raise ValueError(f"Error reading file: {str(e)}")


def clean_json_response(raw: str) -> str:
    """Removes markdown-style ```json ... ``` blocks and trims whitespace."""
    try:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
        return match.group(1).strip() if match else raw.strip()
    except Exception as e:
        import traceback; traceback.print_exc();
        raise ValueError(f"Error cleaning JSON response: {str(e)}")