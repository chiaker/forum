const app = () => {
  const state = {
    topics: [],
    posts: []
  };

	const openBtn = document.getElementById('openBtn');
	const closeBtn = document.getElementById('closeBtn');

	const openModal = () => {
		document.querySelector('.modal_input').value = '';
		form.style.display = 'flex';
	}

	const closeModal = () => {
		form.style.display = 'none';
	}

	openBtn.addEventListener('click', openModal);
	closeBtn.addEventListener('click', closeModal);

  const loadTopics = () => {
   fetch("/api/v1/topics")
    .then(response => response.json())
    .then(data => {
      state.topics = data;
      renderTopic();
    })
    .catch(error => {
      console.error("Ошибка загрузки тем:", error);
    });
  };

	// Для постов

//  const loadPosts = (topicId) => {
//    fetch(`/api/v1/topics/${topicId}/posts`)
//      .then(response => response.json())
//      .then(data => {
//        state.posts = data;
//        renderPost();
//      })
//      .catch(error => {
//        console.error("Ошибка загрузки постов:", error);
//      });
//  };

  const renderTopic = () => {
    const root = document.getElementById('topic-list');
    root.innerHTML = "";

    state.topics.forEach((topic) => {
      root.innerHTML += `
			<div class="post-item" id="${topic.id}">
        <h2 class="post-item__title">${topic.title}</h2>
        <span class="post-item__text-contant">${topic.content}</span>
      </div>
			
			`
    });
  };

	// Для постов

//  const renderPost = () => {
//    const root = document.getElementById('post-list');
//    root.innerHTML = "";
//
//    state.posts.forEach((post) => {
//      const col = document.createElement('div');
//      col.className = "col-md-6";
//
//      const card = document.createElement('div');
//      card.className = "card h-100";
//
//      const cardBody = document.createElement('div');
//      cardBody.className = "card-body";
//
//      const content = document.createElement('p');
//      content.className = "card-text";
//      content.textContent = post.content;
//
//      cardBody.append(content);
//      card.append(cardBody);
//      col.append(card);
//      root.append(col);
//    });
//  };

  loadTopics();

	const form = document.getElementById('addTopicForm');
	const modalContent = document.querySelector('.modal_content');

	form.addEventListener('submit', (e) => {
		e.preventDefault();

		const formData = new FormData(form);

		const topicTitle = formData.get('topicTitle');
		const topicContent = formData.get('content');

		const jsonData = {
			content: topicContent || 'content',
			title: topicTitle
		}

		fetch(form.action, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(jsonData)
		})

		loadTopics();
		closeModal();
	})
	
	form.addEventListener('click', (e) => {
  	if (!modalContent.contains(e.target)) {
    	closeModal();
  	}
	});
};

app();