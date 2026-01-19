function inc(btn) {
    const qty = btn.previousElementSibling;
    let val = parseInt(qty.dataset.qty);
    val++;
    qty.dataset.qty = val;
    qty.innerText = val;
}

function dec(btn) {
    const qty = btn.nextElementSibling;
    let val = parseInt(qty.dataset.qty);
    if (val > 0) val--;
    qty.dataset.qty = val;
    qty.innerText = val;
}
