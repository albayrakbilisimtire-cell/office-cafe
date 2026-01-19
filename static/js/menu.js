let orderCache = [];

function inc(btn) {
    const qty = btn.previousElementSibling;
    qty.innerText = Number(qty.innerText) + 1;
}

function dec(btn) {
    const qty = btn.nextElementSibling;
    const v = Number(qty.innerText);
    if (v > 0) qty.innerText = v - 1;
}

function submitOrder() {
    orderCache = [];

    document.querySelectorAll(".product").forEach(p => {
        const product = p.dataset.name;
        p.querySelectorAll(".opt").forEach(opt => {
            const qty = Number(opt.querySelector(".qty").innerText);
            if (qty > 0) {
                const option = opt.querySelector("span").innerText;
                orderCache.push({ product, option, qty });
            }
        });
    });

    if (orderCache.length === 0) {
        alert("Ürün seçmediniz");
        return;
    }

    document.getElementById("roomModal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("roomModal").classList.add("hidden");
}

function confirmOrder() {
    const room = document.getElementById("finalRoom").value;
    if (!room) {
        alert("Oda seçmelisiniz");
        return;
    }

    fetch("/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room, order: orderCache })
    }).then(r => {
        if (r.ok) {
            alert("Sipariş alındı");
            location.reload();
        } else {
            alert("Sipariş kaydedilemedi");
        }
    });
}
