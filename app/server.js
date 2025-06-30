const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Конфигурация Yandex GPT
const YANDEX_GPT_API_KEY = 'AQVN3DLCJDp1u2jptt77paTsBGU0gQK1mM9qn4A5';
const YANDEX_GPT_FOLDER_ID = 'b1g1cve9cg3ncb768ota';

// Проверка наличия ключей при старте
if (!YANDEX_GPT_API_KEY || !YANDEX_GPT_FOLDER_ID) {
  console.error('ОШИБКА: Не заданы YANDEX_GPT_API_KEY или YANDEX_GPT_FOLDER_ID');
  process.exit(1);
}

// Генерация объявления
app.post('/generate-ad', async (req, res) => {
  try {
    const {
      propertyType,
      area,
      rooms,
      location,
      price,
      advantages,
      infrastructure,
      additional
    } = req.body;

    // Валидация входных данных
    if (!propertyType || !area || !location || !price) {
      return res.status(400).json({ error: 'Не заполнены обязательные поля' });
    }

    // Формируем промпт
    const prompt = `Создай объявление для Авито о ${propertyType} в формальном стиле, но с душой. Без форматирования по жирности текста. Перечисления параметров обозначай дефисом. Параметры:
- Площадь: ${area} м²
- Комнат: ${rooms}
- Район: ${location}
- Цена: ${price} руб.
${advantages ? `Преимущества: ${advantages}\n` : ''}
${infrastructure ? `Инфраструктура: ${infrastructure}\n` : ''}
${additional ? `Дополнительно: ${additional}\n` : ''}
В конце добавь подвал с таким текстом:
Центр недвижимости #1
Ваш надежный партнер в сфере недвижимости
- Покупка/продажа
- Аренда
- Ипотека
- Юрсопровождение
- Новостройки`;

    // Вызов Yandex GPT API
    const response = await axios.post(
      'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
      {
        modelUri: `gpt://${YANDEX_GPT_FOLDER_ID}/yandexgpt/latest`,
        completionOptions: {
          stream: false,
          temperature: 0.6,
          maxTokens: 2000
        },
        messages: [
          {
            role: "system",
            text: "Ты профессиональный риелтор, который пишет объявления для Авито."
          },
          {
            role: "user",
            text: prompt
          }
        ]
      },
      {
        headers: {
          'Authorization': `Api-Key ${YANDEX_GPT_API_KEY}`,
          'x-folder-id': YANDEX_GPT_FOLDER_ID,
          'Content-Type': 'application/json'
        },
        timeout: 10000 // 10 секунд таймаут
      }
    );

    // Проверка ответа
    if (!response.data.result || !response.data.result.alternatives) {
      throw new Error('Некорректный ответ от Yandex GPT');
    }

    const adText = response.data.result.alternatives[0].message.text;
    res.json({ adText });

  } catch (error) {
    console.error('Ошибка генерации объявления:', error.message);
    
    // Детализация ошибок API
    if (error.response) {
      console.error('Статус:', error.response.status);
      console.error('Данные:', error.response.data);
    }
    
    res.status(500).json({ 
      error: 'Ошибка генерации объявления',
      details: error.message 
    });
  }
});

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Сервер запущен на порту ${PORT}`);
  console.log(`Используется Folder ID: ${YANDEX_GPT_FOLDER_ID}`);
});