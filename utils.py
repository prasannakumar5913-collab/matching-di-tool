<<<<<<< HEAD
import pandas as pd
import io

def format_validation_results(results):
    # Dummy summary as DataFrame
    summary = []
    for check, issues in results.items():
        summary.append({'Check': check, 'Issues Found': len(issues)})
    return pd.DataFrame(summary)

def export_report(df, results):
    # Dummy Excel export: just returns the original dataframe as Excel bytes
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
=======
import pandas as pd
import io

def format_validation_results(results):
    # Dummy summary as DataFrame
    summary = []
    for check, issues in results.items():
        summary.append({'Check': check, 'Issues Found': len(issues)})
    return pd.DataFrame(summary)

def export_report(df, results):
    # Dummy Excel export: just returns the original dataframe as Excel bytes
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
>>>>>>> b33c5470e587ca56ea1ef7ed1f693479d30c8f68
    return output