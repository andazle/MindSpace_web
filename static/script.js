document.addEventListener('DOMContentLoaded', function () {
    const panel = document.getElementById('accessibility-panel');
    const enableBtn = document.getElementById('enable-accessibility');
    const closeBtn = document.getElementById('close-panel');
    const resetBtn = document.getElementById('reset-settings');
    const fontDecrease = document.getElementById('font-decrease');
    const fontIncrease = document.getElementById('font-increase');
    const colorBtns = document.querySelectorAll('.color-btn');
    const toggleImagesBtn = document.getElementById('toggle-images');

    // Текущие настройки
    let settings = {
        enabled: false,
        fontSizeMultiplier: 1,
        colorScheme: 'default',
        imagesHidden: false
    };

    // Загрузка настроек
    function loadSettings() {
        const saved = localStorage.getItem('accessibility');
        if (saved) {
            try {
                settings = JSON.parse(saved);
                // Применяем стили, если режим был включен
                if (settings.enabled) {
                    applySettings();
                    panel.style.display = 'block';
                }
            } catch (e) {
                console.error('Ошибка загрузки настроек', e);
            }
        }
    }

    // Сохранение настроек
    function saveSettings() {
        localStorage.setItem('accessibility', JSON.stringify(settings));
    }

    // Функция включения/выключения режима
    function enableMode(status) {
        settings.enabled = status;
        panel.style.display = status ? 'block' : 'none';

        if (!status) {
            // Если выключаем — сбрасываем всё к стандарту
            settings.fontSizeMultiplier = 1;
            settings.colorScheme = 'default';
            settings.imagesHidden = false;
        }

        applySettings();
        saveSettings();
    }

    // Применение настроек к документу
    function applySettings() {
        // Установка множителя шрифта
        document.documentElement.style.setProperty('--font-size-multiplier', settings.fontSizeMultiplier);

        // Установка цветовой схемы
        // Удаляем старые классы схем
        document.body.classList.remove('color-scheme-black-yellow', 'color-scheme-black-white');
        if (settings.colorScheme !== 'default') {
            document.body.classList.add(`color-scheme-${settings.colorScheme}`);
        }

        // Скрытие/показ изображений
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.style.display = settings.imagesHidden ? 'none' : 'block';
        });
    }

    // --- Обработчики событий ---

    // Кнопка включения в меню (base.html)
    if (enableBtn) {
        enableBtn.addEventListener('click', (e) => {
            e.preventDefault();
            enableMode(true);
        });
    }

    // Исправленная кнопка закрытия (крестик)
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            // Теперь при нажатии на крестик режим полностью выключается
            // и больше не "вылетает" на других страницах
            enableMode(false);
        });
    }

    // Кнопка "Обычная версия"
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            enableMode(false);
        });
    }

    // Изменение шрифта
    if (fontDecrease) {
        fontDecrease.addEventListener('click', () => {
            if (settings.fontSizeMultiplier > 0.8) {
                settings.fontSizeMultiplier = Math.round((settings.fontSizeMultiplier - 0.1) * 10) / 10;
                applySettings();
                saveSettings();
            }
        });
    }

    if (fontIncrease) {
        fontIncrease.addEventListener('click', () => {
            if (settings.fontSizeMultiplier < 2) {
                settings.fontSizeMultiplier = Math.round((settings.fontSizeMultiplier + 0.1) * 10) / 10;
                applySettings();
                saveSettings();
            }
        });
    }

    // Выбор цветовой схемы
    if (colorBtns.length) {
        colorBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                settings.colorScheme = btn.dataset.scheme;
                applySettings();
                saveSettings();
            });
        });
    }

    // Скрытие изображений
    if (toggleImagesBtn) {
        toggleImagesBtn.addEventListener('click', () => {
            settings.imagesHidden = !settings.imagesHidden;
            applySettings();
            saveSettings();
        });
    }

    // Инициализация при загрузке
    loadSettings();
});