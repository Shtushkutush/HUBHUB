document.getElementById('adForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const form = e.target;
  const loading = document.getElementById('loading');
  const result = document.getElementById('result');
  
  // Показать индикатор загрузки
  form.classList.add('hidden');
  loading.classList.remove('hidden');
  result.classList.add('hidden');
  
  // Собрать данные из формы
  const formData = {
    propertyType: document.getElementById('propertyType').value,
    area: document.getElementById('area').value,
    rooms: document.getElementById('rooms').value,
    location: document.getElementById('location').value,
    price: document.getElementById('price').value,
    advantages: document.getElementById('advantages').value,
    infrastructure: document.getElementById('infrastructure').value,
    additional: document.getElementById('additional').value
  };
  
  try {
    // Отправить запрос на сервер
    const response = await fetch('/generate-ad', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при генерации объявления');
    }
    
    const data = await response.json();
    
    // Показать результат
    document.getElementById('adContent').textContent = data.adText;
    loading.classList.add('hidden');
    result.classList.remove('hidden');
    
    // Кнопка копирования
    document.getElementById('copyBtn').addEventListener('click', function() {
      navigator.clipboard.writeText(data.adText)
        .then(() => {
          const btn = document.getElementById('copyBtn');
          btn.textContent = 'Скопировано!';
          setTimeout(() => {
            btn.textContent = 'Копировать текст';
          }, 2000);
        })
        .catch(err => {
          console.error('Ошибка при копировании: ', err);
        });
    });
    
  } catch (error) {
    console.error('Ошибка:', error);
    loading.classList.add('hidden');
    form.classList.remove('hidden');
    alert('Произошла ошибка при генерации объявления. Пожалуйста, попробуйте еще раз.');
  }
});