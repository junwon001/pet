// -------------------------
// 공통
// -------------------------
const API_BASE = "http://127.0.0.1:8000";

// -------------------------
// 홈
// -------------------------

async function showHome() {
  const userId = localStorage.getItem("user_id");

  if (!userId) {
    renderLogin();   // ❗ showLogin ❌
    return;
  }

  // 🔹 최신 BCS
  const latestRes = await fetch(`/bcs/latest/user/${userId}`);
  const latest = await latestRes.json();

  // 🔹 BCS 히스토리
  const historyRes = await fetch(`/bcs/history/user/${userId}`);
  const history = await historyRes.json();

  let bcsText = "기록 없음";
  let color = "#999";

  if (latest && latest.bcs !== null) {
    bcsText = `BCS ${latest.bcs}`;
    if (latest.bcs >= 8) color = "#e74c3c";
    else if (latest.bcs >= 6) color = "#f39c12";
    else color = "#2ecc71";
  }

  document.getElementById("content").innerHTML = `
      <h2>홈</h2>
      
    </div>
      <p>반려동물 건강 관리 서비스입니다.</p>
      <p>BCS 예측, 사료 추천, 상담 기능을 이용할 수 있습니다.</p>
    </div>

    <div class="card" style="text-align:center;">
      <h3>최근 체형 상태</h3>
      <h1 style="color:${color}">${bcsText}</h1>
      <small>${latest?.created_at ?? ""}</small>
    </div>

    <div class="card">
      <h3>BCS 변화 추이</h3>
      <canvas id="bcsChart" height="200"></canvas>
    </div>
  `;

  if (!history || history.length === 0) return;

  const labels = history.map(h =>
    new Date(h.date).toLocaleDateString()
  );
  const data = history.map(h => h.bcs);

  const ctx = document.getElementById("bcsChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "BCS",
        data: data,
        borderColor: "#3498db",
        backgroundColor: "rgba(52,152,219,0.2)",
        tension: 0.3,
        pointRadius: 5
      }]
    },
    options: {
      scales: {
        y: {
          min: 1,
          max: 9,
          ticks: { stepSize: 1 }
        }
      }
    }
  });
}
function updateNav() {
  const userId = localStorage.getItem("user_id");
  document.getElementById("logout-btn").style.display =
    userId ? "inline-block" : "none";
}


function showSignup() {
  document.getElementById("content").innerHTML = `
    <h2>회원가입</h2>
    <input id="email" placeholder="이메일"><br><br>
    <input id="password" type="password" placeholder="비밀번호"><br><br>

    <button onclick="signup()">회원가입</button>
    <br><br>
    <button onclick="showLogin()">로그인으로 돌아가기</button>
  `;
}

async function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
   // 이메일 형식 검사
  if (!email.includes("@")) {
    alert("이메일 형식이 올바르지 않습니다.");
    return;
  }

  //  비밀번호 길이 검사
  if (password.length < 6) {
    alert("비밀번호는 6자 이상이어야 합니다.");
    return;
  }

  // 너무 쉬운 비밀번호 방지
  if (!/[0-9]/.test(password)) {
    alert("비밀번호에 숫자를 하나 이상 포함해주세요.");
    return;
  }
  const res = await fetch("/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    alert("회원가입 실패");
    return;
  }

  alert("회원가입 완료! 로그인해주세요.");
  showLogin();
}


function showLogin() {
  hideBottomNav();   // 로그인 화면에서 숨김
  document.getElementById("content").innerHTML = `
    <h2>로그인</h2>
    <input id="email" placeholder="이메일"><br>
    <input id="password" type="password" placeholder="비밀번호"><br><br>
    <button onclick="login()">로그인</button>
    <br><br>
    <button onclick="showSignup()">회원가입</button>
  `;
}

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
   // 이메일 형식 검사
  if (!email.includes("@")) {
    alert("이메일 형식이 올바르지 않습니다.");
    return;
  }

  // 비밀번호 길이 검사
  if (password.length < 6) {
    alert("비밀번호는 6자 이상이어야 합니다.");
    return;
  }
  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    alert("로그인 실패");
    return;
  }

  const data = await res.json();

  // user_id 저장
  localStorage.setItem("user_id", data.user_id);

  showBottomNav();

  //  홈으로 이동
  showHome();
}

function logout() {
  // 로그인 정보 제거
  localStorage.removeItem("user_id");
  hideBottomNav(); //바 숨김
  

  // (선택) 다른 상태 값 있으면 같이 제거
  // localStorage.clear();  // 전체 초기화하고 싶으면 이거

  // 로그인 화면으로 이동
  showLogin();
}

function renderLogin() {
  hideBottomNav();
  document.getElementById("content").innerHTML = `
    <h2>로그인</h2>
    <input id="email" placeholder="이메일">
    <input id="password" type="password">
    <button onclick="login()">로그인</button>
    <br><br>
    <button onclick="showSignup()">회원가입</button>
  `;
}

function showBottomNav() {
  document.querySelector(".bottom-nav").style.display = "flex";
}

function hideBottomNav() {
  document.querySelector(".bottom-nav").style.display = "none";
}


// -------------------------
// BCS 입력 / 예측
// -------------------------
function showBCS() {
    const content = document.getElementById("content");

    content.innerHTML = `
        <div class="container">
            <div class="card">
                <h2>BCS 예측</h2>

                <label>체중 (kg)</label>
                <input type="number" id="weight" placeholder="예: 8.5">

                <label>나이 (세)</label>
                <input type="number" id="age" placeholder="예: 5">

                <label>품종</label>
                <input type="text" id="breed" placeholder="예: 말티즈">

                <label>성별</label>
                <select id="sex">
                    <option value="수컷">수컷</option>
                    <option value="중성화 수컷">중성화 수컷</option>
                    <option value="암컷">암컷</option>
                    <option value="중성화 암컷">중성화 암컷</option>
                </select>

                <label>운동량 (시간/일)</label>
                <input type="number" id="exercise" placeholder="예: 1.5">

                <label>하루 사료량 (g)</label>
                <input type="number" id="food_amount" placeholder="예: 180">

                <label>하루 식사 횟수 (회)</label>
                <input type="number" id="food_count" placeholder="예: 2">


                <label>하루 간식량 (g)</label>
                <input type="number" id="snack_amount" placeholder="예: 20">

                <button onclick="submitBCS()">BCS 예측하기</button>
            </div>

            <div id="bcs-result" class="result-card"></div>
        </div>
    `;
}

function submitBCS() {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
        alert("로그인이 필요합니다.");
        showLogin();
        return;
    }
    const weight = parseFloat(document.getElementById("weight").value);
    const age = parseInt(document.getElementById("age").value);
    const breed = document.getElementById("breed").value.trim();
    const sex = document.getElementById("sex").value;

    const exercise = parseFloat(document.getElementById("exercise").value);
    const foodAmount = parseFloat(document.getElementById("food_amount").value);
    const foodCount = parseInt(document.getElementById("food_count").value);
    const snackAmount = parseFloat(document.getElementById("snack_amount").value);

    // 🔴 필수값 검증
    if (isNaN(weight) || weight <= 0) {
        alert("체중은 0보다 큰 값이어야 합니다.");
        return;
    }

    if (isNaN(age) || age <= 0) {
        alert("나이는 1 이상이어야 합니다.");
        return;
    }

    if (!breed) {
        alert("품종을 입력해주세요.");
        return;
    }

    // 🔴 선택값 검증
    if (!isNaN(exercise) && exercise < 0) {
        alert("운동량은 음수가 될 수 없습니다.");
        return;
    }

    if (!isNaN(foodAmount) && foodAmount < 0) {
        alert("사료량은 음수가 될 수 없습니다.");
        return;
    }
    if (!isNaN(foodCount) && foodCount <= 0) {
      alert("식사 횟수는 1회 이상이어야 합니다.");
      return;
    } 

    

    if (!isNaN(snackAmount) && snackAmount < 0) {
        alert("간식량은 음수가 될 수 없습니다.");
        return;
    }

    const data = {
        user_id: userId,
        weight: weight,
        age: age,
        breed: breed,
        sex: sex,
        exercise: isNaN(exercise) ? null : exercise,
        food_amount: isNaN(foodAmount) ? null : foodAmount,
        food_count: isNaN(foodCount) ? null : foodCount,
        snack_amount: isNaN(snackAmount) ? null : snackAmount
    };

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        document.getElementById("bcs-result").innerText =
        `BCS 결과: ${result.raw_result.bcs_class}\n\n${result.raw_result.advice}`;
})
    .catch(err => {
        document.getElementById("bcs-result").innerText =
            "❌ 예측 중 오류 발생";
        console.error(err);
    });
}




async function predictBCS() {
    const data = {
        weight: parseFloat(document.getElementById("weight").value),
        age: parseInt(document.getElementById("age").value),
        breed: document.getElementById("breed").value,
        sex: document.getElementById("sex").value,
        exercise: parseFloat(document.getElementById("exercise").value)
    };

    const response = await fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    const resultDiv = document.getElementById("result");

    // 🔥🔥🔥 바로 여기
    resultDiv.innerHTML = `
        <h3>BCS 결과</h3>
        <p>등급: ${result.bcs_class}</p>
        <p>${result.advice}</p>
    `;
}


// -------------------------
// 상담 (임시 화면)
// -------------------------
function showConsult() {
  document.getElementById("content").innerHTML = `
    <div class="card">
      <h2>💬 AI 수의 상담</h2>

      <textarea id="consult-question"
        placeholder="궁금한 증상이나 질문을 입력하세요"
        style="width:100%; height:120px;"></textarea>

      <br><br>

      <select id="consult-dept">
        <option value="">전체</option>
        <option value="내과">내과</option>
        <option value="치과">치과</option>
        <option value="안과">안과</option>
        <option value="치과">치과</option>
        <option value="피부과">피부과</option>
      </select>

      <br><br>
      <button onclick="submitConsult()">상담하기</button>

      <div id="consult-result" style="margin-top:20px;"></div>
    </div>
  `;
}

async function submitConsult() {
  const question = document.getElementById("consult-question").value;
  const department = document.getElementById("consult-dept").value;

  if (!question.trim()) {
    alert("질문을 입력해주세요.");
    return;
  }

  const res = await fetch("/consult", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: question,
      department: department || null
    })
  });

  const data = await res.json();

  document.getElementById("consult-result").innerHTML = `
    <h3>💡 상담 결과</h3>
    <p style="white-space: pre-line;">${data.answer}</p>
  `;
}


// -------------------------
// 사료 추천
// -------------------------
async function showFeed() {
  document.getElementById("content").innerHTML = `
    <div class="card">
      <h2>사료 추천</h2>
      <p>추천 결과를 불러오는 중...</p>
    </div>
  `;

  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("로그인이 필요합니다.");
    showLogin();
    return;
  }

  const res = await fetch(`/recommend/${userId}`);
  const data = await res.json();

  console.log("추천 데이터:", data);

  if (data.error) {
    document.getElementById("content").innerHTML = `
      <div class="card">
        <h2>사료 추천</h2>
        <p>❌ ${data.error}</p>
      </div>
    `;
    return;
  }

  if (!data.recommended_feeds || data.recommended_feeds.length === 0) {
    document.getElementById("content").innerHTML = `
      <div class="card">
        <h2>사료 추천</h2>
        <p>추천 사료가 없습니다.</p>
      </div>
    `;
    return;
  }

  let html = `
    <div class="card">
      <h2>사료 추천</h2>
    </div>
  `;

  data.recommended_feeds.forEach(feed => {
    html += `
      <div class="feed-card">
        <img class="feed-image" src="${feed.image}" alt="사료 이미지">
        <div class="feed-info">
          <div class="feed-badges">
            <span class="badge badge-bcs">BCS ${data.bcs} 맞춤</span>
          </div>
          <h4 class="feed-title">${feed.title}</h4>
          <p class="feed-price">${feed.price.toLocaleString()}원</p>
          <p class="feed-reason">
             ${feed.recommend_reason ?? "현재 상태에 적합한 사료입니다."}
          </p>
          <a href="${feed.link}" target="_blank" class="feed-link">
            상품 보러가기 →
          </a>
        </div>
      </div>
    `;
  });

  document.getElementById("content").innerHTML = html;
}



// -------------------------
// 시설 (미구현)
// -------------------------
function showFacility() {
    document.getElementById("content").innerHTML = `
        <div class="card">
            <h2>📍 관련 시설</h2>
            <p>지도 기반 시설 기능 (추후 구현)</p>
        </div>
    `;
}

// -------------------------
// 마이페이지 (미구현)
// -------------------------
function showMyPage() {
    document.getElementById("content").innerHTML = `
        <div class="card">
            <h2>👤 마이페이지</h2>
            <p>로그인 / 반려동물 정보 관리 (추후 구현)</p>
        </div>
    `;
}

// -------------------------
// 초기 화면
// -------------------------
window.onload = () => {
  const userId = localStorage.getItem("user_id");

  if (userId) {
    showBottomNav();
    showHome();
  } else {
    hideBottomNav();
    renderLogin();
  }
};
