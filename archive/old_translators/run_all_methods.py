"""
Run all three translation methods and compare results
"""
import time
import os
from method1_redact_replace import translate_pdf_method1
from method2_decompose_rebuild import translate_pdf_method2
from method3_reportlab import translate_pdf_method3

def get_file_size(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    return "N/A"

def main():
    input_pdf = r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - LÉGENDES ET NOTES GÉNÉRALES.pdf"

    outputs = {
        "Method 1 (Redact)": r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - METHOD1 - REDACT.pdf",
        "Method 2 (Decompose)": r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - METHOD2 - DECOMPOSE.pdf",
        "Method 3 (ReportLab)": r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - METHOD3 - REPORTLAB.pdf"
    }

    methods = [
        ("Method 1 (Redact)", translate_pdf_method1),
        ("Method 2 (Decompose)", translate_pdf_method2),
        ("Method 3 (ReportLab)", translate_pdf_method3)
    ]

    results = {}

    print("\n" + "="*80)
    print("PDF TRANSLATION - COMPARING 3 METHODS")
    print("="*80)
    print(f"\nOriginal file: {input_pdf}")
    print(f"Original size: {get_file_size(input_pdf)}")
    print("\n")

    for method_name, method_func in methods:
        print("\n" + "="*80)
        output_path = outputs[method_name]

        try:
            start_time = time.time()
            method_func(input_pdf, output_path)
            elapsed_time = time.time() - start_time

            results[method_name] = {
                "success": True,
                "time": elapsed_time,
                "size": get_file_size(output_path),
                "path": output_path
            }

        except Exception as e:
            print(f"\nERROR in {method_name}: {e}")
            results[method_name] = {
                "success": False,
                "error": str(e)
            }

    # Print summary
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)

    print(f"\n{'Method':<25} {'Status':<12} {'Time':<12} {'Size':<12}")
    print("-" * 80)

    for method_name, result in results.items():
        if result["success"]:
            status = "[OK] Success"
            time_str = f"{result['time']:.2f}s"
            size_str = result['size']
        else:
            status = "[X] Failed"
            time_str = "N/A"
            size_str = "N/A"

        print(f"{method_name:<25} {status:<15} {time_str:<12} {size_str:<12}")

    print("\n" + "="*80)
    print("OUTPUT FILES:")
    print("="*80)
    for method_name, result in results.items():
        if result["success"]:
            print(f"\n{method_name}:")
            print(f"  {result['path']}")

    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("""
Method 1 (Redact & Replace):
  + Properly removes original text using redaction
  + Clean approach, built-in PyMuPDF feature
  - May lose some font formatting

Method 2 (Decompose & Rebuild):
  + Rebuilds page from scratch, maximum control
  + Can preserve graphics and layout elements
  - Complex, may miss some elements
  - Longer processing time

Method 3 (ReportLab):
  + Uses original page as background image
  + Guaranteed visual preservation
  - Larger file size (image-based)
  - Text is not truly editable in PDF
    """)

    print("\n[OK] All methods completed! Please review the output PDFs.")

if __name__ == "__main__":
    main()
