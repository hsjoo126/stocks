document.addEventListener("DOMContentLoaded", function () {
    const searchBox = document.getElementById("search-box");
    const resultBox = document.getElementById("autocomplete-results");
    let selectedIndex = -1; 

    // 자동완성 기능
    searchBox.addEventListener("input", function () {
        let query = searchBox.value.trim();
        selectedIndex = -1; //검색어 입력 시 선택 초기화

        if (query === "") {
            resultBox.innerHTML = "";
            resultBox.style.display = "none";
            return;
        }

        fetch(`/autocomplete/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                resultBox.innerHTML = ""; // 기존 목록 초기화

                if (data.length > 0) {
                    data.forEach((stock, index) => {
                        let item = document.createElement("a");
                        item.textContent = stock;
                        item.href = `/stocks/${stock}/`;
                        item.classList.add("autocomplete-item");
                        resultBox.appendChild(item);
                    });

                    resultBox.style.display = "block";

                    //첫 번째 항목 자동 선택
                    selectedIndex = 0;
                    updateSelection(document.querySelectorAll(".autocomplete-item"));
                } else {
                    resultBox.style.display = "none";
                }
            })
            .catch(error => console.error("에러 발생:", error));
    });

    //방향키로 검색 결과 선택
    searchBox.addEventListener("keydown", function (event) {
        let items = document.querySelectorAll(".autocomplete-item");

        if (items.length === 0) return; // 검색 결과가 없으면 무시

        if (event.key === "ArrowDown") {
            event.preventDefault();
            selectedIndex = (selectedIndex + 1) % items.length;
            updateSelection(items);
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateSelection(items);
        } else if (event.key === "Enter") {
            event.preventDefault();
            if (selectedIndex >= 0) {
                window.location.href = items[selectedIndex].href;
            }
        }
    });

    // 선택된 항목 스타일 + 스크롤 이동
    function updateSelection(items) {
        items.forEach(item => item.classList.remove("active"));
        if (selectedIndex >= 0) {
            items[selectedIndex].classList.add("active");
            items[selectedIndex].scrollIntoView({ block: "nearest", behavior: "smooth" }); // 스크롤 이동
        }
    }

    // 검색어를 지워도 검색창 유지
    searchBox.addEventListener("focus", function () {
        resultBox.style.display = "block";
    });

    // 새로고침 시 메인 페이지로 이동
    if (window.location.pathname === "/") {
        window.location.replace("/stocks/main/");
    }
});
