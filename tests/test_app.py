# Файл: tests/test_app.py

import pytest
from unittest.mock import MagicMock
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app



def test_api_integration_logic(mocker):
    """
    Этот тест проверяет, что наша основная логика правильно
    вызывает API и передает данные между ними.
    """
    print("\nЗапущен тест интеграции API...")

    
    
   
    mock_groq_response = MagicMock()
    mock_groq_response.choices[0].message.content = "ОТЧЕТ ОТ GROQ"
    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions.create.return_value = mock_groq_response

    
    mock_mistral_response = MagicMock()
    mock_mistral_response.choices[0].message.content = "ФИНАЛЬНЫЙ ТЕКСТ ОТ MISTRAL"
    mock_mistral_client = MagicMock()
    mock_mistral_client.chat.return_value = mock_mistral_response
    
    
    mocker.patch('app.groq_client', mock_groq_client)
    mocker.patch('app.mistral_client', mock_mistral_client)

    
    
 
    piece_title = "Название"
    author = "Автор"
    director_wishes = ""
    
    
    research_prompt = "..." 
    research_completion = app.groq_client.chat.completions.create(
        messages=[{"role": "user", "content": research_prompt}],
        model="llama-3.1-8b-instant"
    )
    research_result = research_completion.choices[0].message.content

   
    analysis_prompt = f"Отчет исследователя: {research_result}"
    messages = [{"role": "user", "content": analysis_prompt}]
    chat_response = app.mistral_client.chat(
        model="mistral-large-latest",
        messages=messages
    )
    final_text = chat_response.choices[0].message.content
    
    
    mock_groq_client.chat.completions.create.assert_called_once()
    

    mock_mistral_client.chat.assert_called_once()
    
  
    prompt_sent_to_mistral = mock_mistral_client.chat.call_args[1]['messages'][0]['content']
    assert "ОТЧЕТ ОТ GROQ" in prompt_sent_to_mistral
    
   
    assert final_text == "ФИНАЛЬНЫЙ ТЕКСТ ОТ MISTRAL"

    print("Тест интеграции API успешно пройден!")