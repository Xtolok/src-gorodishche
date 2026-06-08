(function () {
  var STORAGE = {
    enabled: 'a11y-enabled',
    fontSize: 'a11y-font-size',
    theme: 'a11y-theme',
    images: 'a11y-images',
  };

  var FONT_STEPS = [100, 125, 150, 175, 200];
  var THEMES = ['yellow', 'light', 'dark'];

  var root = document.documentElement;
  var toggle = document.getElementById('a11y-toggle');
  var controls = document.getElementById('a11y-controls');
  var fsDown = document.getElementById('a11y-fs-down');
  var fsUp = document.getElementById('a11y-fs-up');
  var fsValue = document.getElementById('a11y-fs-value');
  var imagesBtn = document.getElementById('a11y-images');
  var liveRegion = document.getElementById('a11y-live');
  var themeButtons = document.querySelectorAll('[data-a11y-theme]');

  function readStorage(key, fallback) {
    try {
      var value = localStorage.getItem(key);
      return value === null ? fallback : value;
    } catch (e) {
      return fallback;
    }
  }

  function writeStorage(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {}
  }

  function announce(message) {
    if (liveRegion) {
      liveRegion.textContent = message;
    }
  }

  function isEnabled() {
    return root.classList.contains('a11y-mode');
  }

  function getFontIndex() {
    var size = parseInt(readStorage(STORAGE.fontSize, '100'), 10);
    var index = FONT_STEPS.indexOf(size);
    return index === -1 ? 0 : index;
  }

  function applyFontSize(index) {
    index = Math.max(0, Math.min(FONT_STEPS.length - 1, index));
    var size = FONT_STEPS[index];
    root.dataset.a11yFontSize = String(size);
    if (fsValue) {
      fsValue.textContent = size + '%';
    }
    if (fsDown) {
      fsDown.disabled = index === 0;
    }
    if (fsUp) {
      fsUp.disabled = index === FONT_STEPS.length - 1;
    }
    writeStorage(STORAGE.fontSize, String(size));
  }

  function applyTheme(theme) {
    if (THEMES.indexOf(theme) === -1) {
      theme = 'yellow';
    }
    root.dataset.a11yTheme = theme;
    themeButtons.forEach(function (button) {
      var active = button.getAttribute('data-a11y-theme') === theme;
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    writeStorage(STORAGE.theme, theme);
  }

  function applyImages(show) {
    root.classList.toggle('a11y-hide-images', !show);
    if (imagesBtn) {
      imagesBtn.setAttribute('aria-pressed', show ? 'true' : 'false');
      imagesBtn.textContent = show ? 'Изображения: вкл.' : 'Изображения: выкл.';
    }
    writeStorage(STORAGE.images, show ? '1' : '0');
  }

  function updateToggleLabel() {
    if (!toggle) {
      return;
    }
    toggle.setAttribute('aria-pressed', isEnabled() ? 'true' : 'false');
    toggle.textContent = isEnabled()
      ? 'Обычная версия сайта'
      : 'Версия для слабовидящих';
  }

  function setEnabled(enabled) {
    root.classList.toggle('a11y-mode', enabled);
    if (controls) {
      controls.hidden = !enabled;
    }
    if (!enabled) {
      root.classList.remove('a11y-hide-images');
      delete root.dataset.a11yFontSize;
      delete root.dataset.a11yTheme;
    }
    writeStorage(STORAGE.enabled, enabled ? '1' : '0');
    updateToggleLabel();
    if (enabled) {
      applyFontSize(getFontIndex());
      applyTheme(readStorage(STORAGE.theme, 'yellow'));
      applyImages(readStorage(STORAGE.images, '1') !== '0');
      announce('Включена версия для слабовидящих');
    } else {
      announce('Включена обычная версия сайта');
    }
  }

  if (toggle) {
    var legacyEnabled = readStorage('a11y-visually-impaired', '0') === '1';
    if (legacyEnabled && readStorage(STORAGE.enabled, '0') === '0') {
      writeStorage(STORAGE.enabled, '1');
    }
    if (readStorage(STORAGE.enabled, '0') === '1') {
      setEnabled(true);
    } else {
      if (controls) {
        controls.hidden = true;
      }
      updateToggleLabel();
    }

    toggle.addEventListener('click', function () {
      setEnabled(!isEnabled());
    });
  }

  if (fsDown) {
    fsDown.addEventListener('click', function () {
      applyFontSize(getFontIndex() - 1);
      announce('Размер шрифта ' + FONT_STEPS[getFontIndex()] + '%');
    });
  }

  if (fsUp) {
    fsUp.addEventListener('click', function () {
      applyFontSize(getFontIndex() + 1);
      announce('Размер шрифта ' + FONT_STEPS[getFontIndex()] + '%');
    });
  }

  themeButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      applyTheme(button.getAttribute('data-a11y-theme'));
      announce('Цветовая схема изменена');
    });
  });

  if (imagesBtn) {
    imagesBtn.addEventListener('click', function () {
      var show = imagesBtn.getAttribute('aria-pressed') !== 'true';
      applyImages(show);
      announce(show ? 'Изображения показаны' : 'Изображения скрыты');
    });
  }
})();
