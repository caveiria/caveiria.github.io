// botão "Copiar prompt"
document.querySelectorAll(".copiar").forEach(function (b) {
  b.addEventListener("click", function () {
    var txt = b.parentElement.querySelector("pre").innerText;
    var pronto = function () {
      b.textContent = "Copiado!";
      b.classList.add("ok");
      setTimeout(function () { b.textContent = "Copiar prompt"; b.classList.remove("ok"); }, 1800);
    };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(txt).then(pronto, function () { copiaVelha(txt); pronto(); });
    } else { copiaVelha(txt); pronto(); }
  });
});
function copiaVelha(txt) {
  var t = document.createElement("textarea");
  t.value = txt; document.body.appendChild(t); t.select();
  try { document.execCommand("copy"); } catch (e) {}
  t.remove();
}

// vídeos agendados aparecem sozinhos na lista quando chega a hora
document.querySelectorAll(".card[data-sai]").forEach(function (c) {
  if (Date.now() >= Date.parse(c.dataset.sai)) {
    c.removeAttribute("data-sai");
    c.hidden = false;
  }
});

// busca na página inicial
var busca = document.getElementById("busca");
if (busca) {
  busca.addEventListener("input", function () {
    var q = busca.value.trim().toLowerCase();
    var achou = 0;
    document.querySelectorAll(".card").forEach(function (c) {
      var ok = !c.dataset.sai && (!q || c.dataset.busca.indexOf(q) !== -1);
      c.hidden = !ok;
      if (ok) achou++;
    });
    document.getElementById("vazio").hidden = achou > 0;
  });
}

// faíscas laranja/osso quando copia o prompt
document.querySelectorAll(".copiar").forEach(function (b) {
  b.addEventListener("click", function () {
    if (!document.documentElement.classList.contains("anim")) return;
    var r = b.getBoundingClientRect();
    for (var i = 0; i < 12; i++) {
      var f = document.createElement("span");
      var ang = Math.random() * Math.PI * 2, dist = 30 + Math.random() * 40;
      f.className = "faisca";
      f.style.left = (r.left + r.width / 2) + "px";
      f.style.top = (r.top + r.height / 2) + "px";
      f.style.background = i % 2 ? "#F07F23" : "#EDE3CF";
      f.style.setProperty("--dx", Math.cos(ang) * dist + "px");
      f.style.setProperty("--dy", Math.sin(ang) * dist + "px");
      document.body.appendChild(f);
      setTimeout(function (el) { el.remove(); }, 750, f);
    }
  });
});

// cartões e seções aparecem quando chegam na tela
(function () {
  if (!document.documentElement.classList.contains("anim")) return;
  var alvos = document.querySelectorAll(".card, .cartao h2");
  document.querySelectorAll(".card").forEach(function (c) { c.classList.add("revelar"); });
  if (!("IntersectionObserver" in window)) {
    alvos.forEach(function (el) { el.classList.add("visto"); });
    return;
  }
  var lote = 0;
  var obs = new IntersectionObserver(function (entradas) {
    lote = 0;
    entradas.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.style.setProperty("--atraso", (lote++ * 0.08) + "s");
      e.target.classList.add("visto");
      obs.unobserve(e.target);
    });
  }, { threshold: 0.15 });
  alvos.forEach(function (el) { obs.observe(el); });
})();
