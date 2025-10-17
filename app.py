# ======================================================================================
# ISIDA: Ассистент режиссера (V10.0 - Финальный релиз на основе стабильной версии)
# ======================================================================================

import streamlit as st
from groq import Groq
from mistralai.client import MistralClient
import os
import re
from dotenv import load_dotenv

load_dotenv()

IZI_METHODOLOGY_OPTIMIZED = """
**1. Изучение действительности времени:**
- Исследуй эпоху написания: какой период, что происходило, исторические события, личности у власти, перевороты, революции.
- Проанализируй биографию автора в контексте написания произведения. Найди параллели между его жизнью и текстом, ищи неочевидные или спорные факты.

**2. Анализ самого произведения:**
- Проанализируй название (если это необходимо).
- Определи ключевые события (не более 5):
    - **Исходное событие:** Катализатор, произошедший ДО начала пьесы, "за занавесом". Что запустило всю историю?
    - **Сюжетообразующее событие:** Ключевой поворот, который меняет всё и запускает основной сюжет.
    - **Центральное событие:** Смысловой экватор пьесы, точка невозврата.
    - **Главное (кульминационное) событие:** Момент разрешения основного конфликта, где кристально ясна идея автора.
    - **Финальное событие:** Маленький штрих в конце, который закольцовывает историю или придает ей новый смысл.
- **ВАЖНОЕ ПРАВИЛО:** Событие должно влиять на ВСЕХ персонажей, хотя бы косвенно. Иначе это просто факт.

**3. Тема и Идея:**
- **Тема:** О чём это? (То, что изображено: любовь, семья, война).
- **Идея:** Что автор думает по поводу этой темы? (Глубокая, развернутая мысль).

**4. Конфликт:**
- Сформулируй как противостояние сущностей ОДНОЙ КАТЕГОРИИ (А1 против А2), а не "человек против общества".
- Раздели на типы: Внешний (влияет на всех), Внутренний (внутри героя), Основной.

**5. Сверхзадача:**
- **Сверхзадача автора:** Ради чего глобально автор это написал? Какое его главное послание?
- **Сверхзадача режиссера:** Предложи 2-3 смелых, современных варианта, ради чего это ставить СЕЙЧАС.
"""

st.set_page_config(layout="wide", page_title="ISIDA: Ассистент режиссера")
st.title("🎭 ISIDA: Ассистент режиссера")

GROQ_API_KEY = os.getenv('GROQ_API_KEY') or st.secrets.get('GROQ_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY') or st.secrets.get('MISTRAL_API_KEY')

try:
    if not GROQ_API_KEY or not MISTRAL_API_KEY:
        st.error("API ключи не найдены. Пожалуйста, добавьте их в .env файл или в Secrets на Streamlit Cloud.")
        st.stop()
    groq_client = Groq(api_key=GROQ_API_KEY)
    mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
except Exception as e:
    st.error(f"Ошибка инициализации API клиентов: {e}")
    st.stop()

def clean_markdown_for_copy(markdown_text):
    """Очищает markdown-разметку для чистого копирования в .docx."""
    text = re.sub(r'#+\s', '', markdown_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = text.replace('---', '\n')
    text = re.sub(r'\|.*\|', '', text) 
    text = re.sub(r'-\|', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def custom_copy_button(text_to_copy, button_text):
    """Генерирует HTML/JS для кастомной кнопки копирования."""
   
    element_id = "text-to-copy-" + str(hash(text_to_copy))
    
    
    button_html = f"""
    <div id="{element_id}" style="display: none;">{text_to_copy}</div>
    <button onclick="copyToClipboard_{element_id}()">
        {button_text}
    </button>
    <script>
    function copyToClipboard_{element_id}() {{
        const text = document.getElementById('{element_id}').innerText;
        navigator.clipboard.writeText(text).then(() => {{
            alert('Текст скопирован!');
        }}, (err) => {{
            alert('Ошибка копирования. Попробуйте вручную.');
        }});
    }}
    </script>
    """
    st.markdown(button_html, unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.5, 2, 0.5])

with col2:
    st.header("Материал для анализа")
    piece_title = st.text_input("**Название пьесы:**")
    author = st.text_input("**Автор:**")

    st.subheader("Дополнительные установки (необязательно)")
    director_wishes = st.text_area(
        "Пожелания для исследования:", 
        placeholder="Пример: 'Найди информацию о феминистском движении в ту эпоху' или 'Сделай акцент на экономических причинах конфликтов'."
    )

    if st.button("🚀 Создать экспликацию"):
        if not all([piece_title, author]):
            st.warning("Пожалуйста, заполните название пьесы и имя автора.")
        else:
            final_text = ""
            try:
                
                with st.spinner("Этап 1/2: Исследователь (Groq) ищет контекст..."):
                    research_prompt = (
                        f"Проведи детальное исследование для пьесы '{piece_title}' автора {author}. "
                        "Используй свои поисковые возможности. Найди и структурируй в виде краткого отчета: "
                        "1. Точный год написания и исторический контекст этой эпохи. "
                        "2. Ключевые, неочевидные факты из биографии автора, связанные с написанием пьесы.\n"
                        f"ОСОБОЕ ВНИМАНИЕ удели следующему пожеланию: '{director_wishes if director_wishes else 'Без особых пожеланий'}'. "
                        "Ищи точные, проверенные факты."
                    )
                    
                    research_completion = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": research_prompt}],
                        model="llama-3.1-8b-instant" 
                    )
                    research_result = research_completion.choices[0].message.content
                    st.info("✅ Контекст найден!")
               
                with st.spinner("Этап 2/2: Аналитик (Mistral) пишет экспликацию..."):
                    analysis_prompt = (
                        f"Ты — высококлассный ассистент театрального режиссера. Напиши полную режиссерскую "
                        f"экспликацию для пьесы '{piece_title}' автора {author}.\n\n"
                        "Для пункта 1 ('Изучение времени') используй отчет исследователя. "
                        "Для остального — свои внутренние знания о тексте пьесы.\n\n"
                        f"НЕУКОСНИТЕЛЬНО следуй методологии режиссера Изи:\n{IZI_METHODOLOGY_OPTIMIZED}\n\n"
                        f"ОТЧЕТ ИССЛЕДОВАТЕЛЯ:\n{research_result}\n\n"
                        "Сгенерируй финальный, отформатированный markdown-документ."
                    )
                    
                    messages = [{"role": "user", "content": analysis_prompt}]
                    
                    chat_response = mistral_client.chat(
                        model="mistral-large-latest",
                        messages=messages
                    )
                    final_text = chat_response.choices[0].message.content

                st.header("✅ Готовая экспликация:")
                
                if final_text:
                    clean_text = clean_markdown_for_copy(final_text)                   
                    custom_copy_button(clean_text, "📋 Скопировать весь текст")
                    
                    st.download_button(
                        label="📥 Скачать всю экспликацию (.txt)",
                        data=clean_text,
                        file_name=f"Экспликация_{piece_title}.txt",
                        mime="text/plain"
                    )

                st.subheader("Анализ по разделам:")
                sections = re.split(r'\n---\n', final_text) 
                for i, section in enumerate(sections):
                    if section.strip():                        
                        cleaned_section_text = clean_markdown_for_copy(section)
                        title_match = re.search(r'#+\s*(.*)', cleaned_section_text)                        
                        title_for_file = title_match.group(1).strip() if title_match and title_match.group(1).strip() else f"Раздел_{i+1}"
                        
                        display_title_match = re.search(r'#+\s*(.*)', section)
                        display_title = display_title_match.group(1).strip() if display_title_match else "Дополнительно"

                        with st.expander(f"**{display_title}**", expanded=(display_title.startswith("РЕЖИССЁРСКАЯ"))):                            
                            st.download_button(
                                label=f"📥 Скачать раздел '{title_for_file}'",
                                data=cleaned_section_text,
                                file_name=f"{piece_title}_{title_for_file}.txt",
                                mime="text/plain",
                                key=f"download_button_{i}" 
                            )
                            st.markdown("---") 
                            st.markdown(section, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Произошла ошибка во время генерации: {e}")

    st.markdown("<br><br><br>", unsafe_allow_html=True) 
    st.markdown("---")    
    st.markdown("""
        <div style='text-align: center; color: grey;'>
            Made with ☕️ and ❤️ for Izi.<br>
            Поделиться обратной связью можно <a href="https://t.me/LaSiddhartha" target="_blank" style="color: #888; text-decoration: underline;">в Telegram</a>.
        </div>
    """, unsafe_allow_html=True)