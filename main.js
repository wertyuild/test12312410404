// Ocean wave animation
(function oceanWave() {
  const canvas = document.getElementById('ocean-bg');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width = window.innerWidth;
  let height = window.innerHeight;
  canvas.width = width;
  canvas.height = height;
  let points = [];
  const POINTS = 40;
  for (let i = 0; i < POINTS; i++) {
    points.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3
    });
  }
  function draw() {
    ctx.clearRect(0, 0, width, height);
    let grad = ctx.createLinearGradient(0, 0, width, height);
    grad.addColorStop(0, 'rgba(255,255,255,0.25)');
    grad.addColorStop(1, 'rgba(65, 90, 119, 0.25)');
    for (let i = 0; i < POINTS; i++) {
      for (let j = i + 1; j < POINTS; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 180) {
          ctx.strokeStyle = grad;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(points[i].x, points[i].y);
          ctx.lineTo(points[j].x, points[j].y);
          ctx.stroke();
        }
      }
    }
    for (let i = 0; i < POINTS; i++) {
      ctx.beginPath();
      ctx.arc(points[i].x, points[i].y, 3, 0, 2 * Math.PI);
      ctx.fillStyle = 'rgba(255,255,255,0.85)';
      ctx.shadowColor = '#fff';
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }
  function animate() {
    for (let i = 0; i < POINTS; i++) {
      points[i].x += points[i].vx;
      points[i].y += points[i].vy;
      if (points[i].x < 0 || points[i].x > width) points[i].vx *= -1;
      if (points[i].y < 0 || points[i].y > height) points[i].vy *= -1;
    }
    draw();
    requestAnimationFrame(animate);
  }
  animate();
  window.addEventListener('resize', () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
  });
})();

// Покупка: шаг 1 — ввод username и проверка через API
const form = document.getElementById('buy-form');
const usernameInput = document.getElementById('username');
const userCard = document.getElementById('user-card');
const buyOptions = document.getElementById('buy-options');
let currentUsername = '';

form.addEventListener('submit', async function(e) {
  e.preventDefault();
  let username = usernameInput.value.trim();
  if (username.startsWith('@')) {
    username = username.slice(1); // убираем @
  }
  if (!username) return;
  userCard.innerHTML = 'Проверка...';
  userCard.style.display = 'block';
  userCard.classList.add('fade-in');
  buyOptions.style.display = 'none';
  // Проверка пользователя
  try {
    const resp = await fetch('http://localhost:9000/api/check_user', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username})
    });   
    const data = await resp.json();
    if (!data.ok) throw new Error(data.error || data.detail || 'Ошибка');
    // Обновляем ник и аватарку в step2
    document.getElementById('displayUsername').textContent = '@' + data.username;
    document.getElementById('displayAvatar').src = `http://localhost:9000/api/avatar?username=${data.username}`;
    currentUsername = data.username; // Сохраняем username для использования в оплате
    // Переключаем шаги
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
  } catch (err) {
    // Показываем ошибку
    userCard.innerHTML = '<span style="color:#ff6666">Пользователь не найден</span>';
    setTimeout(() => { userCard.style.display = 'none'; }, 2000);
  }
});

function showBuyOptions() {
  userCard.style.display = 'none';
  buyOptions.style.display = 'flex';
  buyOptions.classList.add('fade-in');
  buyOptions.innerHTML = `
    <div class="buy-stars-block">
      <label for="stars-range">Выберите количество звёзд</label>
      <input type="range" min="1" max="1000" value="1" id="stars-range">
      <div style="display:flex;align-items:center;gap:10px;margin-top:10px;">
        <input type="number" min="1" max="1000" value="1" id="stars-input" style="width:70px;text-align:center;">
        <span style="font-size:22px;">⭐</span>
        <span style="font-size:18px;">=</span>
        <span id="stars-price" style="font-size:22px;font-weight:600;">1.27</span>
        <span style="font-size:18px;">₽</span>
      </div>
    </div>
    <div class="pay-methods-block">
      <label style="margin-top:20px;display:block;">Выберите способ оплаты</label>
      <div class="pay-methods">
        <button data-method="cryptobot" class="button" data-tooltip="CryptoBot: комиссия 3%">CryptoBot <div class="pay-desc">BTC, ETH, USDT и другое<br>Комиссия: 3%</div></button>
        <button data-method="lzt" class="button" data-tooltip="LOLZ MARKET: комиссия 5%">LOLZ MARKET <div class="pay-desc">Баланс аккаунта<br>Комиссия: 5%</div></button>
      </div>
    </div>
    <div style="margin-top:15px;display:flex;gap:10px;">
      <button class="change-btn"><span>Изменить</span></button>
      <div class="button confirm" id="final-confirm" data-tooltip="Оплатить заказ">
        <div class="button-wrapper">
          <div class="text">Оплатить</div>
          <span class="icon">
            <svg viewBox="0 0 16 16" class="bi bi-cart2" fill="currentColor" height="16" width="16" xmlns="http://www.w3.org/2000/svg">
              <path d="M0 2.5A.5.5 0 0 1 .5 2H2a.5.5 0 0 1 .485.379L2.89 4H14.5a.5.5 0 0 1 .485.621l-1.5 6A.5.5 0 0 1 13 11H4a.5.5 0 0 1-.485-.379L1.61 3H.5a.5.5 0 0 1-.5-.5zM3.14 5l1.25 5h8.22l1.25-5H3.14zM5 13a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0zm9-1a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0z"></path>
            </svg>
          </span>
        </div>
      </div>
    </div>
  `;
  let selectedStars = 1;
  let selectedMethod = null;
  const starsRange = buyOptions.querySelector('#stars-range');
  const starsInput = buyOptions.querySelector('#stars-input');
  const starsPrice = buyOptions.querySelector('#stars-price');
  starsRange.oninput = function() {
    starsInput.value = starsRange.value;
    selectedStars = parseInt(starsRange.value);
    starsPrice.textContent = (selectedStars * 1.27).toFixed(2);
  };
  starsInput.oninput = function() {
    let v = parseInt(starsInput.value);
    if (isNaN(v) || v < 1) v = 1;
    if (v > 1000) v = 1000;
    starsInput.value = v;
    starsRange.value = v;
    selectedStars = v;
    starsPrice.textContent = (selectedStars * 1.27).toFixed(2);
  };
  buyOptions.querySelectorAll('.pay-methods button').forEach(btn => {
    btn.onclick = () => {
      buyOptions.querySelectorAll('.pay-methods button').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedMethod = btn.getAttribute('data-method');
    };
  });
  buyOptions.querySelector('.change-btn').onclick = () => {
    buyOptions.style.display = 'none';
    userCard.style.display = 'block';
  };
  buyOptions.querySelector('#final-confirm').onclick = async () => {
    if (!selectedStars || !selectedMethod) {
      alert('Выберите количество звёзд и способ оплаты!');
      return;
    }
    if (selectedMethod === 'cryptobot') {
      // Создаём заказ на бэкенде и получаем order_id
      const resp = await fetch('http://localhost:9000/api/buy', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          username: currentUsername,
          stars: selectedStars,
          payment_method: 'cryptobot'
        })
      });
      const data = await resp.json();
      if (data.ok && data.order_id) {
        // Генерируем ссылку на CryptoBot с payload (order_id)
        const payload = encodeURIComponent('order_' + data.order_id);
        const url = `https://t.me/CryptoBot?start=shop-${payload}`;
        window.open(url, '_blank');
        alert('После оплаты вернитесь на сайт для подтверждения!');
      } else {
        alert('Ошибка создания заказа!');
      }
    } else {
      alert(`Заказ: @${currentUsername}, ${selectedStars} звёзд, способ: ${selectedMethod}`);
    }
  };
}

// Плавная анимация появления
const style = document.createElement('style');
style.innerHTML = `.fade-in {animation: fadeIn 0.5s;}
@keyframes fadeIn {from {opacity:0;transform:translateY(30px);} to {opacity:1;transform:translateY(0);}}`;
document.head.appendChild(style); 