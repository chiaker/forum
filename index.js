const app = () => {
  const state = {
    topics: [],
    posts: []
  };


  const loadTopics = () => {
    fetch("http://192.168.0.69:8000/api/v1/topics")
      .then(response => response.json())
      .then(data => {
        state.topics = data;
        renderTopic();
      })
      .catch(error => {
        console.error("Ошибка загрузки тем:", error);
      });
  };

  const loadPosts = (topicId) => {
    fetch(`http://192.168.0.69:8000/api/v1/topics/${topicId}/posts`)
      .then(response => response.json())
      .then(data => {
        state.posts = data;
        renderPost(); // только здесь вызываем
      })
      .catch(error => {
        console.error("Ошибка загрузки постов:", error);
      });
  };

  const renderTopic = () => {
    const root = document.getElementById('topic-list');
    root.innerHTML = "";

    state.topics.forEach((topic) => {
      const item = document.createElement('button');
      item.className = "btn btn-outline-primary";
      item.textContent = topic.title;
      item.id = topic.id;
      item.addEventListener('click', () => {
        loadPosts(topic.id);
      });
      root.append(item);
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

  loadTopics();

	
};

app();