import re
import html
import streamlit as st
from docx import Document


TAB_MARKER = "<tab>"


def convert_footnotes(text: str) -> str:
    """
    Превращает (*текст сноски) в <footnote>текст сноски</footnote>
    """
    return re.sub(
        r"\(\*([^)]+)\)",
        lambda m: f"<footnote>{html.escape(m.group(1).strip())}</footnote>",
        text
    )


def run_to_ficbook(run) -> str:
    """
    Конвертирует кусочек текста Word с его стилями:
    курсив, жирный, зачёркнутый.
    """
    text = run.text

    if not text:
        return ""

    text = html.escape(text)

    if run.font.strike:
        text = f"<s>{text}</s>"

    if run.bold:
        text = f"<b>{text}</b>"

    if run.italic:
        text = f"<i>{text}</i>"

    return text


def paragraph_to_ficbook(paragraph) -> str:
    """
    Конвертирует абзац.
    Пустые строки сохраняются.
    Непустые абзацы получают <tab>.
    """
    text = "".join(run_to_ficbook(run) for run in paragraph.runs)
    text = convert_footnotes(text)

    if text.strip():
        return TAB_MARKER + text

    return ""


def docx_to_ficbook(uploaded_file) -> str:
    doc = Document(uploaded_file)

    paragraphs = []

    for paragraph in doc.paragraphs:
        paragraphs.append(paragraph_to_ficbook(paragraph))

    return "\n".join(paragraphs)


st.set_page_config(
    page_title="DOCX → Ficbook",
    page_icon="📚",
    layout="wide"
)

st.title("📚 DOCX → Ficbook")
st.caption("Конвертер вордовского файла в разметку Фикбука: <tab>, <i>, <b>, <s>, <footnote>.")

uploaded_file = st.file_uploader(
    "Загрузи .docx файл",
    type=["docx"]
)

if uploaded_file is not None:
    try:
        result = docx_to_ficbook(uploaded_file)

        st.success("Готово! Можно копировать или скачать файл.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Символов с пробелами", len(result))

        with col2:
            st.metric("Символов без пробелов", len(result.replace(" ", "").replace("\n", "")))

        with col3:
            st.metric("Слов", len(re.findall(r"\w+", result)))

        st.text_area(
            "Готовый текст для Фикбука",
            value=result,
            height=500
        )

        output_name = uploaded_file.name.rsplit(".", 1)[0] + "_ficbook.txt"

        st.download_button(
            label="Скачать .txt",
            data=result,
            file_name=output_name,
            mime="text/plain"
        )

    except Exception as e:
        st.error("Что-то пошло не так. Файл точно .docx?")
        st.exception(e)
else:
    st.info("Загрузи Word-файл, и я превращу его в фикбучную разметку.")