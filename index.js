const app = () => {
  // caskod;sakdljasldk
  const state = {
    topics: [],
    posts: [],
    openedPost: null,
  };

  const openBtn = document.getElementById("openBtn");
  const closeBtn = document.getElementById("closeBtn");
  const form = document.getElementById("addTopicForm");
  const modalContent = document.querySelector(".modal_content");

  const openModal = () => {
    document
      .querySelectorAll(".modal_input")
      .forEach((input) => (input.value = ""));
    form.style.display = "flex";
    form.style.animationName = "modal-open";
  };

  const closeModal = () => {
    form.style.animationName = "modal-close";
    setTimeout(() => (form.style.display = "none"), 100);
  };

  openBtn.addEventListener("click", openModal);
  closeBtn.addEventListener("click", closeModal);

  // 🔻 Загрузка тем
  const loadTopics = () => {

    fetch("/api/v1/topics")
      .then((response) => response.json())
      .then((data) => {
        state.topics = data;
        renderTopic();
      })
      .catch((error) => {
        console.error("Ошибка загрузки тем:", error);
      });
  };

  // 🔻 Загрузка комментариев по id темы
  const loadPosts = (topicId) => {
    fetch(`/api/v1/topics/${topicId}/posts`)
      .then((response) => response.json())
      .then((data) => {
        state.posts = data;
        renderPost(data, topicId);
      })
      .catch((error) => {
        console.error("Ошибка загрузки постов:", error);
      });
  };

  const renderPost = (postList, topicId) => {
    const root = document.getElementById(`postsList_${topicId}`);
    if (!root) return;
    root.innerHTML =
      postList.length > 0
        ? postList
          .map(
            (post) =>
              `<div class="comment" id="comment_${post.id}">${post.content}</div>`
          )
          .join("")
        : "<div class='comment'>Нет комментариев</div>";
  };

  // 🔻 Отрисовка тем
  const renderTopic = () => {
    const root = document.getElementById("topic-list");
    root.innerHTML = ""; // очищаем

    state.topics.forEach((topic) => {
      const topicId = topic.id.toString();

      const item = document.createElement("div");
      item.className = "post-item";
      item.id = topicId;

      item.innerHTML = `
        <h2 class="post-item__title">${topic.title}</h2>
        <span class="post-item__text-contant">${topic.content}</span>
        <section class="comments" id="post_${topicId}" style="display:none">
          <div class="comments-list" id="postsList_${topicId}"></div>
          <form class="comment-add" id="addPostForm_${topicId}" autocomplete="off">
            <input type="text" name="comment" id="addPostContent_${topicId}">
            <input type="submit" value="Send" class="comment-btn">
          </form>
        </section>
      `;

      item.querySelector("h2").addEventListener("click", (e) => {
        e.stopPropagation();

        const isOpen = state.openedPost === topicId;

        if (state.openedPost !== null && state.openedPost !== topicId) {
          const prev = document.getElementById(`post_${state.openedPost}`);
          if (prev) prev.style.display = "none";
        }

        if (!isOpen) {
          const current = document.getElementById(`post_${topicId}`);
          if (current) current.style.display = "flex";
          state.openedPost = topicId;
          loadPosts(topicId);
        } else {
          const current = document.getElementById(`post_${topicId}`);
          if (current) current.style.display = "none";
          state.openedPost = null;
        }
      });

      root.appendChild(item);
    });
  };

  // 🔻 Добавление нового комментария через backend
  document.addEventListener("submit", (e) => {
    if (e.target.classList.contains("comment-add")) {
      e.preventDefault();
      const form = e.target;
      const topicId = form.id.split("_")[1];
      const content = form.querySelector('input[name="comment"]').value.trim();
      const submitBtn = form.querySelector(".comment-btn");
      submitBtn.disabled = true;

      fetch(`/api/v1/topics/${topicId}/posts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: content || "empty comment" }),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Ошибка отправки поста");
          return res.json();
        })
        .then(() => {
          form.reset();
          loadPosts(topicId);
        })
        .catch((err) => console.error(err))
        .finally(() => (submitBtn.disabled = false));
    }
  });

  // 🔻 Создание новой темы через backend
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const topicTitle = form
      .querySelector('input[name="topicTitle"]')
      .value.trim();
    const topicContent = form
      .querySelector('input[name="topicContent"]')
      .value.trim();
    const submitBtn = document.getElementById("submitBtn");
    submitBtn.disabled = true;

    fetch("/api/v1/topics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: topicTitle || "Untitled topic",
        content: topicContent || "No content",
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Ошибка создания темы");
        return res.json();
      })
      .then(() => {
        closeModal();
        loadTopics(); // загружаем заново
      })
      .catch((err) => console.error(err))
      .finally(() => (submitBtn.disabled = false));
  });

  // Закрытие модалки по клику вне формы
  form.addEventListener("click", (e) => {
    if (!modalContent.contains(e.target)) {
      closeModal();
    }
  });

  // 🚀 Старт
  loadTopics();
};

app();