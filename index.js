// Главная функция приложения, которая запускается сразу
const app = () => {
  // Состояние приложения, хранит данные тем и постов
  const state = {
    topics: [],  // Массив для хранения списка тем
    posts: []    // Массив для хранения постов (пока не используется)
  };

  // Получаем кнопки открытия и закрытия модального окна
  const openBtn = document.getElementById('openBtn');
  const closeBtn = document.getElementById('closeBtn');

  // Функция открытия модального окна для создания новой темы
  const openModal = () => {
    document.querySelectorAll('.modal_input').forEach((input => input.value = '')); // Очищаем поля ввода
    form.style.display = 'flex'; // Показываем модальное окно
  };

  // Функция закрытия модального окна
  const closeModal = () => {
    form.style.display = 'none'; // Скрываем модальное окно
  };

  // Вешаем обработчики на кнопки
  openBtn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);

  // Функция загрузки списка тем с сервера
  const loadTopics = () => {
    fetch("/api/v1/topics")
      .then(response => response.json()) // Преобразуем ответ в JSON
      .then(data => {
        state.topics = data; // Сохраняем темы в состояние
        renderTopic(); // Отрисовываем темы
      })
      .catch(error => {
        console.error("Ошибка загрузки тем:", error); // Обработка ошибок
      });
  };

  const loadPosts = (topicId) => {
    fetch(`/api/v1/topics/${topicId}/posts`)
      .then(response => response.json())
      .then(data => {
        state.posts = data;
        renderPost();
      })
      .catch(error => {
        console.error("Ошибка загрузки постов:", error);
      });
  };

  // Функция отрисовки списка тем
  const renderTopic = () => {
    const root = document.getElementById('topic-list'); // Контейнер для тем
    root.innerHTML = ""; // Очищаем контейнер

    // Для каждой темы создаем HTML-элемент
    state.topics.forEach((topic) => {
      root.innerHTML += `
      <div class="post-item" id="${topic.id}">
        <h2 class="post-item__title">${topic.title}</h2>
        <span class="post-item__text-contant">${topic.content}</span>
      </div>
      `;
    });
  };

  const renderPost = () => {
    const root = document.getElementById('post-list');
    root.innerHTML = "";

    state.posts.forEach((post) => {
      const col = document.createElement('div');
      col.className = "col-md-6";

      const card = document.createElement('div');
      card.className = "card h-100";

      const cardBody = document.createElement('div');
      cardBody.className = "card-body";

      const content = document.createElement('p');
      content.className = "card-text";
      content.textContent = post.content;

      cardBody.append(content);
      card.append(cardBody);
      col.append(card);
      root.append(col);
    });
  };

  // Загружаем темы при старте приложения
  loadTopics();

  // Получаем форму и контент модального окна
  const form = document.getElementById('addTopicForm');
  const modalContent = document.querySelector('.modal_content');

  // Обработчик отправки формы
  form.addEventListener('submit', (e) => {
    e.preventDefault(); // Отменяем стандартное поведение формы
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    // Получаем данные из формы
    const formData = new FormData(form);
    const topicTitle = formData.get('topicTitle');
    const topicContent = formData.get('topicContent');

    // Формируем данные для отправки
    const jsonData = {
      content: topicContent || 'content', // Значение по умолчанию
      title: topicTitle
    };

    // Отправляем данные на сервер
    fetch(form.action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(jsonData) // Преобразуем объект в JSON
    })
      .then(() => {
        // Обновляем список тем и закрываем модальное окно
        loadTopics();
        submitBtn.disabled = false;
        closeModal();
      });

  });

  // Закрытие модального окна при клике вне его контента
  form.addEventListener('click', (e) => {
    if (!modalContent.contains(e.target)) {
      closeModal();
    }
  });
};

// Запускаем приложение
app();