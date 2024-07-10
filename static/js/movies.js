//分页加载更多
let visibleMoviesCount = 18; // 最初可见的电影数量
let visibleMovies = []

const movies_page = document.getElementById('movies_page');
const movies_loadMore = document.getElementById('movies_loadMore');

// // 根据可见性计数显示/隐藏电影的函数
function updateVisibility() {
  visibleMovies = document.querySelectorAll('.movies_card');
  debugger
  visibleMovies.forEach((movie, idx) => {
    movie.style.display = idx < visibleMoviesCount ? 'block' : 'none';
  });

  // 如果所有电影都变为可见，则隐藏“加载更多”按钮
  if (visibleMoviesCount >= movies.length) {
    movies_loadMore.style.display = 'none';
  }
}

// “加载更多”按钮点击事件
movies_loadMore.addEventListener('click', () => {
  visibleMoviesCount += 18; // 增加可见数量
  updateVisibility(); // 更新电影可见性
});

// 初始可见性设置
// updateVisibility();


//  搜索方法
function search(e) {
  debugger

 
  document.querySelector(`.dvtjjf.active[data-search="${e.target.dataset.search}"]`)?.classList.remove('active');
  if (e.target.dataset.value) {
    e.target.classList.add('active');
  }
  const searchItems = document.querySelectorAll('.dvtjjf.active');
  const attributes = Array.from(searchItems, searchItem => {
    const property = `data-${searchItem.dataset.search}`;
    const logic = searchItem.dataset.method === 'contain' ? '*' : '^';
    const value = searchItem.dataset.method === 'contain' ? `${searchItem.dataset.value}` : searchItem.dataset.value;
    return `[${property}${logic}='${value}']`;
  });
  const selector = `.movies_card${attributes.join('')}`;
  document.querySelectorAll('.movies_card').forEach(item => item.style.display = 'none');
  document.querySelectorAll(selector).forEach(item => item.style.display = 'block');
}
window.addEventListener('click', function (e) {
  if (e.target.classList.contains('sc-gtsrHT')) {
    e.preventDefault();
    search(e);
  }
});
function sort(e) {
  const sortBy = e.target.dataset.order;
  const style = document.createElement('style');
  style.classList.add('sort-order-style');
  document.querySelector('style.sort-order-style')?.remove();
  document.querySelector('.sort-by-item.active')?.classList.remove('active');
  e.target.classList.add('active');
  if (sortBy === 'rating') {
    const books = Array.from(document.querySelectorAll('.dfdORB'));
    books.sort((bookA, bookB) => {
      const ratingA = parseFloat(bookA.dataset.rating) || 0;
      const ratingB = parseFloat(bookB.dataset.rating) || 0;
      if (ratingA === ratingB) {
        return 0;
      }
      return ratingA > ratingB ? -1 : 1;
    });
    const stylesheet = books.map((book, idx) => `.dfdORB[data-rating="${book.dataset.rating}"] { order: ${idx}; }`).join('\r\n');
    style.innerHTML = stylesheet;
    document.body.appendChild(style);
  }
}
window.addEventListener('click', function (e) {
  if (e.target.classList.contains('sort-by-item')) {
    e.preventDefault();
    sort(e);
  }
});


document.addEventListener('DOMContentLoaded', function() {
            const filterToggle = document.getElementById('filter-toggle');
            const filters = document.getElementById('filters');

            filterToggle.addEventListener('click', function() {
                if (filters.classList.contains('hidden')) {
                    filters.classList.remove('hidden');
                    filters.classList.add('visible');
                } else {
                    filters.classList.remove('visible');
                    filters.classList.add('hidden');
                }
            });
        });


//背景随机视频
document.addEventListener("DOMContentLoaded", function () {
  const videoElement = document.querySelector(".video-source");
  if (videoElement == null) {
    return;
  }

  const videoSource = videoElement.querySelector("source");

  const movieVideos = [
    '../video/video01.mp4',
    '../video/video02.mp4',
    '../video/video03.mp4',
    '../video/video04.mp4',
    '../video/video05.mp4',
    // ...更多电影视频...
  ];

  function playRandomVideo(videos) {
    const randomIndex = Math.floor(Math.random() * videos.length);
    videoSource.src = videos[randomIndex];
    videoElement.load();
  }

  // 初始随机播放一个电影视频
  playRandomVideo(movieVideos);
});