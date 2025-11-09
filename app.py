"""Streamlit PDF Translation App - With Supabase Auth"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from translate_haiku_100 import process_pdf
from auth import require_auth, display_user_info, get_user_id
from supabase_client import get_supabase_client

# Configure page
st.set_page_config(
    page_title="PDF Translator FR→EN",
    page_icon="📄",
    layout="wide"
)

# Require authentication (or allow local mode if Supabase not configured)
require_auth()

# Create necessary directories based on user
user_id = get_user_id()
if user_id:
    # Authenticated user - use user-specific folder
    USER_DIR = Path("user_files") / user_id
    UPLOAD_DIR = USER_DIR / "uploads"
    OUTPUT_DIR = USER_DIR / "translated"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
else:
    # Local testing mode - use shared folder
    UPLOAD_DIR = Path("uploads")
    OUTPUT_DIR = Path("translated_pdfs")
    UPLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

# Title
st.title("Fra to Eng PDF AI Translator")
st.markdown("Translate French architectural PDFs to English")

# Warning
st.warning("⚠️ **Important:** This is an AI-powered translation and may not be 100% accurate. The French version remains the official contractual document.")

# Get API key from environment
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if api_key:
    st.session_state["anthropic_api_key"] = api_key

# Sidebar
with st.sidebar:
    # Display logo
    logo_path = Path("MSDL_Logo_Noir_RGB_HR.png")
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
        # Add custom CSS to remove rounded corners
        st.markdown("""
        <style>
        [data-testid="stImage"] img {
            border-radius: 0px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.divider()
    st.header("⚙️ How it works")
    st.markdown("""
    1. **Upload** French PDF(s)
    2. **Click** Batch Translate
    3. **Download** translated PDFs
    """)

    # Display user info and logout button if authenticated
    display_user_info()

# Main area
tab1, tab2, tab3 = st.tabs(["📤 Upload & Translate", "📁 Files", "📊 History"])

with tab1:
    st.header("Upload PDFs")

    uploaded_files = st.file_uploader(
        "Choose French PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more architectural PDFs in French"
    )

    if uploaded_files:
        st.success(f"✅ Uploaded {len(uploaded_files)} file(s)")

        # Show uploaded files
        for uploaded_file in uploaded_files:
            st.text(f"📄 {uploaded_file.name}")

        st.divider()
        st.header("Batch Translate")

        # Batch translate button
        if st.button("🤖 Batch Translate All Files", type="primary", use_container_width=True):
            if not st.session_state.get("anthropic_api_key"):
                st.error("❌ API Key not found! Set ANTHROPIC_API_KEY environment variable on Render.")
            else:
                import json
                import time

                start_time = time.time()
                progress_bar = st.progress(0)
                status_text = st.empty()
                timer_text = st.empty()

                total_files = len(uploaded_files)
                completed = 0
                total_input_tokens = 0
                total_output_tokens = 0

                for idx, uploaded_file in enumerate(uploaded_files):
                    elapsed = time.time() - start_time
                    timer_text.text(f"⏱️ Elapsed time: {elapsed:.1f}s")
                    status_text.text(f"Processing {uploaded_file.name}...")

                    # Save uploaded file with safe filename (avoid encoding issues)
                    safe_input_name = f"temp_input_{idx}.pdf"
                    input_path = UPLOAD_DIR / safe_input_name
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Generate output filename
                    safe_output_name = f"temp_output_{idx}.pdf"
                    output_path = OUTPUT_DIR / safe_output_name

                    try:
                        # Translate entire PDF with 100% Haiku
                        status_text.text(f"Translating {uploaded_file.name}...")

                        success, input_tokens, output_tokens = process_pdf(
                            str(input_path),
                            str(output_path),
                            st.session_state["anthropic_api_key"]
                        )

                        if success:
                            # Translate filename and add Haiku100 suffix
                            import shutil
                            from anthropic_translator import translate_with_haiku

                            # Extract base name without extension
                            base_name = uploaded_file.name.replace('.pdf', '')

                            # Translate filename using Haiku
                            try:
                                result = translate_with_haiku({"filename": base_name}, st.session_state["anthropic_api_key"])
                                translated_name = result["translations"]["filename"]
                            except:
                                # If translation fails, use original name
                                translated_name = base_name

                            # Create final filename with Haiku100 suffix
                            final_output_name = f"{translated_name} - Haiku100.pdf"
                            final_output_path = OUTPUT_DIR / final_output_name

                            # Move file to final location
                            shutil.move(str(output_path), str(final_output_path))

                            completed += 1
                            total_input_tokens += input_tokens
                            total_output_tokens += output_tokens

                            # Log to database if Supabase is configured
                            user_id = get_user_id()
                            if user_id and st.session_state.get("supabase"):
                                try:
                                    file_size = uploaded_file.size if hasattr(uploaded_file, 'size') else None
                                    st.session_state.supabase.log_translation(
                                        user_id=user_id,
                                        original_filename=uploaded_file.name,
                                        translated_filename=final_output_name,
                                        input_tokens=input_tokens,
                                        output_tokens=output_tokens,
                                        file_size_bytes=file_size,
                                        status="completed"
                                    )
                                except Exception as e:
                                    # Don't fail the translation if logging fails
                                    print(f"Failed to log translation to database: {e}")

                            # Show tokens for this file
                            file_tokens = input_tokens + output_tokens
                            st.success(f"✅ {uploaded_file.name}: {file_tokens:,} tokens ({input_tokens:,} in + {output_tokens:,} out)")
                        else:
                            st.warning(f"⚠️ {uploaded_file.name} needs manual translation - check console")

                        progress_bar.progress(completed / total_files)

                    except Exception as e:
                        st.error(f"❌ Failed to translate {uploaded_file.name}: {e}")
                        completed += 1
                        progress_bar.progress(completed / total_files)
                        continue

                # Final time
                total_time = time.time() - start_time
                minutes = int(total_time // 60)
                seconds = total_time % 60

                if minutes > 0:
                    time_str = f"{minutes}m {seconds:.1f}s"
                else:
                    time_str = f"{seconds:.1f}s"

                # Calculate cost (Haiku 4.5 pricing: $0.80/1M input, $4.00/1M output)
                total_tokens = total_input_tokens + total_output_tokens
                cost_input = (total_input_tokens / 1_000_000) * 0.80
                cost_output = (total_output_tokens / 1_000_000) * 4.00
                total_cost = cost_input + cost_output

                # Show final summary
                status_text.text("")
                timer_text.text(f"⏱️ Total time: {time_str}")
                progress_bar.empty()

                st.success(f"✅ Batch translation complete! Processed {completed}/{total_files} files in {time_str}")

                # Show token usage and cost
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tokens", f"{total_tokens:,}")
                with col2:
                    st.metric("Input", f"{total_input_tokens:,}")
                with col3:
                    st.metric("Output", f"{total_output_tokens:,}")

                st.info(f"💰 Estimated cost: ${total_cost:.4f} USD")
                st.info("📁 Check the 'Files' tab to download your translated PDFs")

with tab2:
    st.header("📁 Translated Files")

    if OUTPUT_DIR.exists():
        pdf_files = list(OUTPUT_DIR.glob("*.pdf"))

        if pdf_files:
            for pdf_file in sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**{pdf_file.name}**")

                with col2:
                    size_mb = pdf_file.stat().st_size / 1024 / 1024
                    st.text(f"{size_mb:.2f} MB")

                with col3:
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="Download",
                            data=f,
                            file_name=pdf_file.name,
                            mime="application/pdf",
                            key=str(pdf_file)
                        )
        else:
            st.info("No translated files yet")

with tab3:
    st.header("📊 Translation History")

    # Only show history if Supabase is configured and user is authenticated
    user_id = get_user_id()
    if user_id and st.session_state.get("supabase"):
        # Get user stats
        try:
            stats = st.session_state.supabase.get_user_stats(user_id)

            # Display statistics
            st.subheader("Your Statistics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Translations", stats.get("total_translations", 0))
            with col2:
                st.metric("Total Tokens", f"{stats.get('total_tokens_used', 0):,}")
            with col3:
                st.metric("Total Cost", f"${stats.get('total_cost_usd', 0):.2f}")

            st.divider()

            # Get translation history
            translations = st.session_state.supabase.get_user_translations(user_id, limit=50)

            if translations:
                st.subheader("Recent Translations")

                for trans in translations:
                    with st.expander(f"📄 {trans['original_filename']} → {trans['translated_filename']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Date:** {trans['created_at'][:10]}")
                            st.markdown(f"**Status:** {trans['status']}")
                            if trans.get('file_size_bytes'):
                                size_mb = trans['file_size_bytes'] / 1024 / 1024
                                st.markdown(f"**File Size:** {size_mb:.2f} MB")

                        with col2:
                            st.markdown(f"**Tokens:** {trans.get('total_tokens', 0):,}")
                            st.markdown(f"**Input:** {trans.get('input_tokens', 0):,}")
                            st.markdown(f"**Output:** {trans.get('output_tokens', 0):,}")
                            st.markdown(f"**Cost:** ${trans.get('cost_total_usd', 0):.4f}")
            else:
                st.info("No translation history yet")

        except Exception as e:
            st.error(f"Failed to load history: {e}")
    else:
        st.info("History is only available when logged in with Supabase")

# Footer
st.divider()
st.markdown("*Production version with Supabase auth (local mode enabled if Supabase not configured)*")
