document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ script.js загружен');

    const panel = document.getElementById('accessibility-panel');
    const enableBtn = document.getElementById('enable-accessibility');
    const closeBtn = document.getElementById('close-panel');
    const resetBtn = document.getElementById('reset-settings');
    const fontDecrease = document.getElementById('font-decrease');
    const fontIncrease = document.getElementById('font-increase');
    const colorBtns = document.querySelectorAll('.color-btn');
    const toggleImagesBtn = document.getElementById('toggle-images');

    console.log('panel:', panel);
    console.log('enableBtn:', enableBtn);

    // Загружаем сохранённые настройки
    let settings = JSON.parse(localStorage.getItem('accessibility')) || {
        enabled: false,
        fontSizeMultiplier: 1,
        colorScheme: 'default',
        imagesHidden: false
    };

    function applySettings() {
        // Изменяем размер шрифта через CSS-переменную
        document.documentElement.style.setProperty('--font-size-multiplier', settings.fontSizeMultiplier);

        // Применяем цветовые схемы
        document.body.classList.remove('color-scheme-black-yellow', 'color-scheme-black-white');
        if (settings.colorScheme !== 'default') {
            document.body.classList.add(`color-scheme-${settings.colorScheme}`);
        }

        // Скрываем/показываем изображения
        document.body.classList.toggle('images-hidden', settings.imagesHidden);

        // Показываем или скрываем панель
        if (panel) {
            panel.style.display = settings.enabled ? 'block' : 'none';
        }
        console.log('Настройки применены:', settings);
    }

    // Функция сохранения в localStorage
    function save() {
        localStorage.setItem('accessibility', JSON.stringify(settings));
    }

    // === Обработчики событий ===
    if (enableBtn) {
        enableBtn.addEventListener('click', (e) => {
            e.preventDefault();
            settings.enabled = true;
            applySettings();
            save();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            settings.enabled = false;
            applySettings();
            save();
        });
    }

    if (fontIncrease) {
        fontIncrease.addEventListener('click', () => {
            if (settings.fontSizeMultiplier < 2.0) {
                settings.fontSizeMultiplier = Math.round((settings.fontSizeMultiplier + 0.1) * 10) / 10;
                applySettings();
                save();
            }
        });
    }

    if (fontDecrease) {
        fontDecrease.addEventListener('click', () => {
            if (settings.fontSizeMultiplier > 0.8) {
                settings.fontSizeMultiplier = Math.round((settings.fontSizeMultiplier - 0.1) * 10) / 10;
                applySettings();
                save();
            }
        });
    }

    if (toggleImagesBtn) {
        toggleImagesBtn.addEventListener('click', () => {
            settings.imagesHidden = !settings.imagesHidden;
            applySettings();
            save();
        });
    }

    colorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            settings.colorScheme = btn.dataset.scheme;
            applySettings();
            save();
        });
    });

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            settings = {
                enabled: true,
                fontSizeMultiplier: 1,
                colorScheme: 'default',
                imagesHidden: false
            };
            applySettings();
            save();
        });
    }

    // Применяем настройки при загрузке страницы
    applySettings();
});