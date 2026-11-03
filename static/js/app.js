(function () {
  "use strict";

  const API = "/api/v1/restaurants";

  function errorText(data, fallback) {
    if (!data) return fallback;
    const detail = data.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((e) => {
          const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : "";
          return field && field !== "body" ? field + ": " + e.msg : e.msg;
        })
        .join(" · ");
    }
    return fallback;
  }

  function showMessage(text, type) {
    const el = document.getElementById("message");
    if (!el) return;
    el.textContent = text;
    el.className = "message " + (type || "");
  }

  async function readJson(response) {
    try {
      return await response.json();
    } catch (_) {
      return null;
    }
  }

  // ---------- Formulario crear / editar ----------
  const form = document.getElementById("restaurant-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const id = form.dataset.id; // si existe, estamos editando
      const raw = Object.fromEntries(new FormData(form));
      const payload = {
        name: (raw.name || "").trim(),
        category: (raw.category || "").trim(),
        city: (raw.city || "").trim(),
        price: Number(raw.price),
        photoUrl: (raw.photoUrl || "").trim() || null,
      };

      const button = form.querySelector("button[type=submit]");
      button.disabled = true;
      showMessage("Guardando…", "");

      try {
        const response = await fetch(id ? API + "/" + id : API, {
          method: id ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await readJson(response);

        if (response.ok) {
          showMessage(id ? "Restaurante actualizado correctamente." : "Restaurante creado correctamente.", "success");
          const msg = id ? "updated" : "created";
          setTimeout(() => {
            window.location.href = "/restaurants/" + data.id + "?msg=" + msg;
          }, 700);
        } else {
          showMessage(errorText(data, "Error al guardar"), "error");
          button.disabled = false;
        }
      } catch (_) {
        showMessage("No se pudo conectar con el servidor.", "error");
        button.disabled = false;
      }
    });
  }

  // ---------- Botón eliminar (detalle) ----------
  document.querySelectorAll("[data-delete-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const name = button.dataset.name || "este restaurante";
      if (!window.confirm('¿Seguro que quieres eliminar "' + name + '"? Esta acción no se puede deshacer.')) {
        return;
      }
      button.disabled = true;
      try {
        const response = await fetch(API + "/" + button.dataset.deleteId, { method: "DELETE" });
        if (response.status === 204) {
          window.location.href = "/?msg=deleted";
        } else {
          const data = await readJson(response);
          showMessage(errorText(data, "No se pudo eliminar"), "error");
          button.disabled = false;
        }
      } catch (_) {
        showMessage("No se pudo conectar con el servidor.", "error");
        button.disabled = false;
      }
    });
  });

  // ---------- Imagen rota -> letra de color ----------
  document.querySelectorAll("img.cover").forEach((img) => {
    img.addEventListener("error", () => {
      const placeholder = document.createElement("div");
      placeholder.className = img.className + " placeholder";
      placeholder.setAttribute("aria-hidden", "true");
      placeholder.textContent = (img.alt.replace("Foto de ", "") || "?").charAt(0);
      img.replaceWith(placeholder);
    });
  });
})();