from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import StaticPage


def static_page_view(request, slug):
    """Представление для отображения статических страниц"""
    page = get_object_or_404(StaticPage, slug=slug, is_active=True)
    
    context = {
        'page': page,
        'title': page.title,
        'meta_description': page.meta_description,
    }
    
    return render(request, 'static_pages/page.html', context)


# Специфичные представления для каждой страницы
def how_to_find_product(request):
    """Как найти товар"""
    try:
        page = StaticPage.objects.get(slug='how-to-find-product', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/how_to_find_product.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Как найти идеальный товар',
            'content': '''
            <div class="hero-section">
                <h2>🔍 Найдите именно то, что ищете!</h2>
                <p class="lead">ShopList делает поиск товаров простым и эффективным. Откройте для себя умные способы найти идеальную покупку!</p>
            </div>
            
            <div class="search-methods">
                <div class="method-card">
                    <div class="method-icon">🎯</div>
                    <h3>Умный поиск</h3>
                    <p>Введите название, бренд или даже описание товара. Наш ИИ поймет, что вы ищете, даже если вы не знаете точного названия!</p>
                    <div class="tip">💡 <strong>Совет:</strong> Попробуйте "красные кроссовки Nike" или "смартфон с хорошей камерой"</div>
                </div>
                
                <div class="method-card">
                    <div class="method-icon">📂</div>
                    <h3>Каталог по категориям</h3>
                    <p>Просматривайте товары по категориям - от электроники до одежды. Удобная навигация поможет быстро найти нужный раздел.</p>
                    <div class="tip">💡 <strong>Совет:</strong> Используйте подкатегории для более точного поиска</div>
                </div>
                
                <div class="method-card">
                    <div class="method-icon">⚡</div>
                    <h3>Фильтры и сортировка</h3>
                    <p>Настройте поиск под себя: цена, бренд, рейтинг, наличие скидок. Найдите лучшее предложение за секунды!</p>
                    <div class="tip">💡 <strong>Совет:</strong> Сохраняйте настройки фильтров для быстрого повторного поиска</div>
                </div>
                
                <div class="method-card">
                    <div class="method-icon">🏷️</div>
                    <h3>Поиск по тегам</h3>
                    <p>Используйте популярные теги: #новинки, #скидки, #хитпродаж, #экологично. Находите тренды и выгодные предложения!</p>
                    <div class="tip">💡 <strong>Совет:</strong> Подписывайтесь на теги, чтобы получать уведомления о новых товарах</div>
                </div>
            </div>
            
            <div class="pro-tips">
                <h3>🚀 Профессиональные советы</h3>
                <div class="tips-grid">
                    <div class="tip-item">
                        <strong>Используйте автодополнение</strong><br>
                        Начните вводить запрос и выберите из предложенных вариантов
                    </div>
                    <div class="tip-item">
                        <strong>Ищите по фото</strong><br>
                        Загрузите изображение товара для поиска похожих предложений
                    </div>
                    <div class="tip-item">
                        <strong>Голосовой поиск</strong><br>
                        Произнесите название товара вместо набора текста
                    </div>
                    <div class="tip-item">
                        <strong>История поиска</strong><br>
                        Возвращайтесь к предыдущим запросам одним кликом
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>Не можете найти нужный товар?</h3>
                <p>Наши эксперты помогут вам! Опишите, что ищете, и мы найдем лучшие варианты.</p>
                <a href="/support/" class="btn btn-primary">Получить помощь</a>
                <a href="/" class="btn btn-outline-primary">Начать поиск</a>
            </div>
            '''
        }
        return render(request, 'static_pages/how_to_find_product.html', context)


def store_addresses(request):
    """Адреса магазинов"""
    try:
        page = StaticPage.objects.get(slug='store-addresses', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/store_addresses.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Наши магазины по всей стране',
            'content': '''
            <div class="hero-section">
                <h2>🏪 Найдите ближайший магазин</h2>
                <p class="lead">Более 500 точек продаж в 150+ городах России. Покупайте онлайн и забирайте в удобном магазине!</p>
            </div>
            
            <div class="store-finder">
                <div class="finder-card">
                    <h3>🔍 Быстрый поиск магазина</h3>
                    <div class="search-form">
                        <input type="text" placeholder="Введите ваш город или адрес" class="form-control">
                        <button class="btn btn-primary">Найти магазины</button>
                    </div>
                </div>
            </div>
            
            <div class="featured-stores">
                <h3>🌟 Флагманские магазины</h3>
                <div class="stores-grid">
                    <div class="store-card premium">
                        <div class="store-badge">Флагман</div>
                        <h4>Москва • ТЦ "Европейский"</h4>
                        <div class="store-info">
                            <p><i class="fas fa-map-marker-alt"></i> пл. Киевского Вокзала, 2</p>
                            <p><i class="fas fa-clock"></i> Ежедневно: 10:00-22:00</p>
                            <p><i class="fas fa-phone"></i> +7 (495) 123-45-67</p>
                            <p><i class="fas fa-car"></i> Бесплатная парковка</p>
                        </div>
                        <div class="store-features">
                            <span class="feature">📱 Зона тестирования</span>
                            <span class="feature">🎧 Аудиозона</span>
                            <span class="feature">☕ Кафе</span>
                        </div>
                        <button class="btn btn-outline-primary">Подробнее</button>
                    </div>
                    
                    <div class="store-card premium">
                        <div class="store-badge">Флагман</div>
                        <h4>СПб • Невский проспект</h4>
                        <div class="store-info">
                            <p><i class="fas fa-map-marker-alt"></i> Невский пр., 28</p>
                            <p><i class="fas fa-clock"></i> Ежедневно: 10:00-23:00</p>
                            <p><i class="fas fa-phone"></i> +7 (812) 987-65-43</p>
                            <p><i class="fas fa-subway"></i> м. Невский проспект</p>
                        </div>
                        <div class="store-features">
                            <span class="feature">🎮 Игровая зона</span>
                            <span class="feature">💻 IT-отдел</span>
                            <span class="feature">🚚 Экспресс-доставка</span>
                        </div>
                        <button class="btn btn-outline-primary">Подробнее</button>
                    </div>
                    
                    <div class="store-card">
                        <h4>Новосибирск • Красный проспект</h4>
                        <div class="store-info">
                            <p><i class="fas fa-map-marker-alt"></i> Красный пр., 153</p>
                            <p><i class="fas fa-clock"></i> Пн-Вс: 9:00-21:00</p>
                            <p><i class="fas fa-phone"></i> +7 (383) 555-12-34</p>
                        </div>
                        <div class="store-features">
                            <span class="feature">📦 Пункт выдачи</span>
                            <span class="feature">🔧 Сервис-центр</span>
                        </div>
                        <button class="btn btn-outline-primary">Подробнее</button>
                    </div>
                    
                    <div class="store-card">
                        <h4>Екатеринбург • Вайнера</h4>
                        <div class="store-info">
                            <p><i class="fas fa-map-marker-alt"></i> ул. Вайнера, 9А</p>
                            <p><i class="fas fa-clock"></i> Пн-Вс: 10:00-20:00</p>
                            <p><i class="fas fa-phone"></i> +7 (343) 777-88-99</p>
                        </div>
                        <div class="store-features">
                            <span class="feature">📱 Трейд-ин</span>
                            <span class="feature">🎁 Подарочная упаковка</span>
                        </div>
                        <button class="btn btn-outline-primary">Подробнее</button>
                    </div>
                </div>
            </div>
            
            <div class="services-section">
                <h3>🎯 Услуги в наших магазинах</h3>
                <div class="services-grid">
                    <div class="service-item">
                        <div class="service-icon">📦</div>
                        <h4>Самовывоз</h4>
                        <p>Заказывайте онлайн и забирайте в любом магазине. Бесплатно и удобно!</p>
                    </div>
                    <div class="service-item">
                        <div class="service-icon">🔧</div>
                        <h4>Сервис и ремонт</h4>
                        <p>Квалифицированный ремонт техники с гарантией качества</p>
                    </div>
                    <div class="service-item">
                        <div class="service-icon">💳</div>
                        <h4>Трейд-ин</h4>
                        <p>Сдайте старую технику и получите скидку на новую покупку</p>
                    </div>
                    <div class="service-item">
                        <div class="service-icon">🎓</div>
                        <h4>Консультации</h4>
                        <p>Эксперты помогут выбрать идеальный товар под ваши потребности</p>
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>Хотите открыть франшизу?</h3>
                <p>Присоединяйтесь к успешной сети ShopList! Поддержка на всех этапах развития бизнеса.</p>
                <a href="/become-partner/" class="btn btn-success">Стать партнером</a>
                <a href="/contacts/" class="btn btn-outline-primary">Связаться с нами</a>
            </div>
            '''
        }
        return render(request, 'static_pages/store_addresses.html', context)


def product_availability(request):
    """Наличие товаров"""
    try:
        page = StaticPage.objects.get(slug='product-availability', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/product_availability.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Всегда в наличии то, что вам нужно',
            'content': '''
            <div class="hero-section">
                <h2>📦 Умная система управления складом</h2>
                <p class="lead">Мы используем ИИ для прогнозирования спроса и поддержания оптимальных запасов. 95% товаров всегда в наличии!</p>
            </div>
            
            <div class="availability-system">
                <h3>🎯 Как работает наша система наличия</h3>
                <div class="system-features">
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h4>Обновление в реальном времени</h4>
                        <p>Информация о наличии обновляется каждые 30 секунд. Вы всегда видите актуальные данные!</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🤖</div>
                        <h4>ИИ-прогнозирование</h4>
                        <p>Искусственный интеллект анализирует тренды и автоматически пополняет популярные товары</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🏪</div>
                        <h4>Мультискладская сеть</h4>
                        <p>15 складов по всей России обеспечивают быструю доставку в любой регион</p>
                    </div>
                </div>
            </div>
            
            <div class="status-guide">
                <h3>🚦 Расшифровка статусов товаров</h3>
                <div class="status-grid">
                    <div class="status-item available">
                        <div class="status-badge success">✅ В наличии</div>
                        <div class="status-info">
                            <h4>Готов к отправке</h4>
                            <p>Товар на складе, отправим в течение 24 часов</p>
                            <div class="delivery-time">🚚 Доставка: 1-3 дня</div>
                        </div>
                    </div>
                    
                    <div class="status-item limited">
                        <div class="status-badge warning">⚠️ Ограниченное количество</div>
                        <div class="status-info">
                            <h4>Торопитесь!</h4>
                            <p>Осталось менее 10 штук. Популярный товар быстро заканчивается</p>
                            <div class="delivery-time">🚚 Доставка: 1-3 дня</div>
                        </div>
                    </div>
                    
                    <div class="status-item preorder">
                        <div class="status-badge info">📅 Под заказ</div>
                        <div class="status-info">
                            <h4>Поставка в пути</h4>
                            <p>Товар уже заказан у поставщика, ожидаем поступление</p>
                            <div class="delivery-time">🚚 Доставка: 5-10 дней</div>
                        </div>
                    </div>
                    
                    <div class="status-item out-of-stock">
                        <div class="status-badge danger">❌ Временно нет</div>
                        <div class="status-info">
                            <h4>Уведомим о поступлении</h4>
                            <p>Оставьте email - сообщим, как только товар появится</p>
                            <div class="delivery-time">📧 Уведомление бесплатно</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="smart-features">
                <h3>🧠 Умные функции для покупателей</h3>
                <div class="features-showcase">
                    <div class="showcase-item">
                        <div class="showcase-icon">🔔</div>
                        <h4>Уведомления о поступлении</h4>
                        <p>Подпишитесь на товар и получите SMS/email, когда он появится в наличии</p>
                        <button class="btn btn-outline-primary">Настроить уведомления</button>
                    </div>
                    
                    <div class="showcase-item">
                        <div class="showcase-icon">📊</div>
                        <h4>История цен и наличия</h4>
                        <p>Смотрите графики изменения цен и частоты поступлений товара</p>
                        <button class="btn btn-outline-primary">Посмотреть аналитику</button>
                    </div>
                    
                    <div class="showcase-item">
                        <div class="showcase-icon">🎯</div>
                        <h4>Альтернативные предложения</h4>
                        <p>Если товара нет, мы предложим похожие варианты с лучшими условиями</p>
                        <button class="btn btn-outline-primary">Найти аналоги</button>
                    </div>
                </div>
            </div>
            
            <div class="guarantee-section">
                <h3>🛡️ Наши гарантии</h3>
                <div class="guarantees">
                    <div class="guarantee-item">
                        <div class="guarantee-icon">💯</div>
                        <h4>Точность информации</h4>
                        <p>Гарантируем 99.5% точность данных о наличии. Если ошиблись - компенсируем доставку</p>
                    </div>
                    <div class="guarantee-item">
                        <div class="guarantee-icon">⏰</div>
                        <h4>Резервирование товара</h4>
                        <p>При оформлении заказа товар резервируется на 24 часа для завершения оплаты</p>
                    </div>
                    <div class="guarantee-item">
                        <div class="guarantee-icon">🔄</div>
                        <h4>Приоритетное пополнение</h4>
                        <p>Популярные товары пополняются в первую очередь на основе вашего спроса</p>
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>Не нашли нужный товар?</h3>
                <p>Наши закупщики найдут и привезут любой товар под заказ. Обычно это занимает 7-14 дней.</p>
                <a href="/contacts/" class="btn btn-primary">Заказать поиск товара</a>
                <a href="/" class="btn btn-outline-primary">Посмотреть каталог</a>
            </div>
            '''
        }
        return render(request, 'static_pages/product_availability.html', context)


def contacts(request):
    """Контакты"""
    try:
        page = StaticPage.objects.get(slug='contacts', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/contacts.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Мы всегда на связи',
            'content': '''
            <div class="hero-section">
                <h2>💬 Свяжитесь с нами любым удобным способом</h2>
                <p class="lead">Наша команда поддержки работает 24/7, чтобы помочь вам в любое время. Средний ответ - 2 минуты!</p>
            </div>
            
            <div class="contact-methods">
                <h3>🚀 Быстрые способы связи</h3>
                <div class="methods-grid">
                    <div class="method-card priority">
                        <div class="method-badge">Самый быстрый</div>
                        <div class="method-icon">💬</div>
                        <h4>Онлайн-чат</h4>
                        <p>Мгновенные ответы от наших экспертов</p>
                        <div class="response-time">⚡ Ответ: 30 секунд</div>
                        <button class="btn btn-primary">Начать чат</button>
                    </div>
                    
                    <div class="method-card">
                        <div class="method-icon">📱</div>
                        <h4>WhatsApp/Telegram</h4>
                        <p>Пишите в мессенджеры - отвечаем быстро</p>
                        <div class="response-time">⚡ Ответ: 2 минуты</div>
                        <div class="messenger-links">
                            <a href="#" class="btn btn-success">WhatsApp</a>
                            <a href="#" class="btn btn-info">Telegram</a>
                        </div>
                    </div>
                    
                    <div class="method-card">
                        <div class="method-icon">📞</div>
                        <h4>Горячая линия</h4>
                        <p>Бесплатные звонки по всей России</p>
                        <div class="phone-number">8 (800) 234-56-78</div>
                        <div class="response-time">🕐 24/7 без выходных</div>
                    </div>
                </div>
            </div>
            
            <div class="contact-departments">
                <h3>🎯 Специализированные отделы</h3>
                <div class="departments-grid">
                    <div class="dept-card">
                        <div class="dept-icon">🛒</div>
                        <h4>Поддержка покупателей</h4>
                        <div class="dept-info">
                            <p>📧 support@shoplist.ru</p>
                            <p>📞 +7 (495) 123-45-67</p>
                            <p>🕐 Круглосуточно</p>
                        </div>
                        <div class="dept-services">
                            <span class="service-tag">Помощь с заказами</span>
                            <span class="service-tag">Возвраты и обмены</span>
                            <span class="service-tag">Техподдержка</span>
                        </div>
                    </div>
                    
                    <div class="dept-card">
                        <div class="dept-icon">🤝</div>
                        <h4>Отдел партнерства</h4>
                        <div class="dept-info">
                            <p>📧 partners@shoplist.ru</p>
                            <p>📞 +7 (495) 987-65-43</p>
                            <p>🕐 Пн-Пт: 9:00-18:00</p>
                        </div>
                        <div class="dept-services">
                            <span class="service-tag">Франшиза</span>
                            <span class="service-tag">B2B продажи</span>
                            <span class="service-tag">Сотрудничество</span>
                        </div>
                    </div>
                    
                    <div class="dept-card">
                        <div class="dept-icon">💼</div>
                        <h4>Корпоративные клиенты</h4>
                        <div class="dept-info">
                            <p>📧 b2b@shoplist.ru</p>
                            <p>📞 +7 (495) 555-77-88</p>
                            <p>🕐 Пн-Пт: 9:00-19:00</p>
                        </div>
                        <div class="dept-services">
                            <span class="service-tag">Оптовые закупки</span>
                            <span class="service-tag">Корп. скидки</span>
                            <span class="service-tag">Персональный менеджер</span>
                        </div>
                    </div>
                    
                    <div class="dept-card">
                        <div class="dept-icon">🔧</div>
                        <h4>Техническая поддержка</h4>
                        <div class="dept-info">
                            <p>📧 tech@shoplist.ru</p>
                            <p>📞 +7 (495) 111-22-33</p>
                            <p>🕐 24/7</p>
                        </div>
                        <div class="dept-services">
                            <span class="service-tag">API интеграции</span>
                            <span class="service-tag">Настройка систем</span>
                            <span class="service-tag">Консультации</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="office-locations">
                <h3>🏢 Наши офисы</h3>
                <div class="offices-grid">
                    <div class="office-card main">
                        <div class="office-badge">Главный офис</div>
                        <h4>Москва</h4>
                        <div class="office-address">
                            <p>📍 Москва-Сити, башня "Федерация"</p>
                            <p>📍 ул. Пресненская наб., 12</p>
                            <p>🚇 м. Выставочная, Деловой центр</p>
                        </div>
                        <div class="office-hours">
                            <p>🕐 Пн-Пт: 9:00-19:00</p>
                            <p>🅿️ Подземная парковка</p>
                            <p>☕ Кафе и переговорные</p>
                        </div>
                    </div>
                    
                    <div class="office-card">
                        <h4>Санкт-Петербург</h4>
                        <div class="office-address">
                            <p>📍 БЦ "Сенатор"</p>
                            <p>📍 Малоохтинский пр., 64</p>
                            <p>🚇 м. Новочеркасская</p>
                        </div>
                        <div class="office-hours">
                            <p>🕐 Пн-Пт: 9:00-18:00</p>
                        </div>
                    </div>
                    
                    <div class="office-card">
                        <h4>Новосибирск</h4>
                        <div class="office-address">
                            <p>📍 БЦ "Гринвич"</p>
                            <p>📍 ул. Фрунзе, 238</p>
                        </div>
                        <div class="office-hours">
                            <p>🕐 Пн-Пт: 10:00-19:00</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="social-media">
                <h3>📱 Мы в социальных сетях</h3>
                <div class="social-grid">
                    <a href="#" class="social-card vk">
                        <div class="social-icon">🔵</div>
                        <h4>ВКонтакте</h4>
                        <p>150K подписчиков</p>
                        <span class="social-tag">Новости и акции</span>
                    </a>
                    <a href="#" class="social-card telegram">
                        <div class="social-icon">✈️</div>
                        <h4>Telegram</h4>
                        <p>75K подписчиков</p>
                        <span class="social-tag">Эксклюзивные скидки</span>
                    </a>
                    <a href="#" class="social-card youtube">
                        <div class="social-icon">📺</div>
                        <h4>YouTube</h4>
                        <p>200K подписчиков</p>
                        <span class="social-tag">Обзоры товаров</span>
                    </a>
                    <a href="#" class="social-card instagram">
                        <div class="social-icon">📸</div>
                        <h4>Instagram</h4>
                        <p>300K подписчиков</p>
                        <span class="social-tag">Lifestyle контент</span>
                    </a>
                </div>
            </div>
            
            <div class="feedback-section">
                <h3>💌 Оставьте отзыв или предложение</h3>
                <div class="feedback-form">
                    <p>Ваше мнение важно для нас! Расскажите, как мы можем стать еще лучше.</p>
                    <div class="form-actions">
                        <button class="btn btn-primary">Написать отзыв</button>
                        <button class="btn btn-outline-primary">Предложить улучшение</button>
                    </div>
                </div>
            </div>
            '''
        }
        return render(request, 'static_pages/contacts.html', context)


def about_company(request):
    """О компании"""
    try:
        page = StaticPage.objects.get(slug='about-company', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/about_company.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'О компании RetailNet Solutions',
            'content': '''
            <div class="hero-section">
                <h2>🚀 Мы создаем будущее розничной торговли</h2>
                <p class="lead">RetailNet Solutions — лидер в области инновационных IT-решений для e-commerce. Более 10 лет мы помогаем бизнесу расти и процветать в цифровую эпоху.</p>
            </div>
            
            <div class="company-story">
                <div class="story-section">
                    <h3>💡 Наша история</h3>
                    <p>Все началось в 2014 году с простой идеи: сделать онлайн-торговлю доступной для каждого бизнеса. Сегодня мы — команда из 200+ профессионалов, которая создает решения мирового уровня.</p>
                </div>
                
                <div class="mission-vision">
                    <div class="mission-card">
                        <h4>🎯 Наша миссия</h4>
                        <p>Демократизировать e-commerce, предоставляя малому и среднему бизнесу инструменты уровня крупных корпораций</p>
                    </div>
                    <div class="vision-card">
                        <h4>🔮 Наше видение</h4>
                        <p>Мир, где каждый предприниматель может легко создать успешный онлайн-бизнес и конкурировать на равных</p>
                    </div>
                </div>
            </div>
            
            <div class="achievements">
                <h3>🏆 Наши достижения</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">1000+</div>
                        <div class="stat-label">Успешных проектов</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">50+</div>
                        <div class="stat-label">Стран присутствия</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">200+</div>
                        <div class="stat-label">Экспертов в команде</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">99.9%</div>
                        <div class="stat-label">Время работы платформы</div>
                    </div>
                </div>
            </div>
            
            <div class="values-section">
                <h3>💎 Наши ценности</h3>
                <div class="values-grid">
                    <div class="value-item">
                        <div class="value-icon">🔬</div>
                        <h4>Инновации</h4>
                        <p>Мы всегда на шаг впереди, внедряя передовые технологии: ИИ, машинное обучение, блокчейн</p>
                    </div>
                    <div class="value-item">
                        <div class="value-icon">🤝</div>
                        <h4>Партнерство</h4>
                        <p>Мы не просто поставщики — мы партнеры в вашем успехе, готовые поддержать на каждом этапе</p>
                    </div>
                    <div class="value-item">
                        <div class="value-icon">⚡</div>
                        <h4>Скорость</h4>
                        <p>Быстрая разработка, молниеносная поддержка, мгновенное масштабирование решений</p>
                    </div>
                    <div class="value-item">
                        <div class="value-icon">🛡️</div>
                        <h4>Надежность</h4>
                        <p>Банковский уровень безопасности, 99.9% uptime, резервное копирование данных</p>
                    </div>
                </div>
            </div>
            
            <div class="team-section">
                <h3>👥 Команда мечты</h3>
                <div class="team-stats">
                    <div class="team-stat">
                        <strong>85%</strong> наших разработчиков имеют опыт 5+ лет
                    </div>
                    <div class="team-stat">
                        <strong>12</strong> сертифицированных архитекторов решений
                    </div>
                    <div class="team-stat">
                        <strong>24/7</strong> техническая поддержка на 8 языках
                    </div>
                </div>
            </div>
            
            <div class="awards-section">
                <h3>🥇 Награды и признание</h3>
                <div class="awards-grid">
                    <div class="award-item">
                        <div class="award-year">2024</div>
                        <div class="award-title">Лучшая E-commerce платформа</div>
                        <div class="award-org">TechCrunch Awards</div>
                    </div>
                    <div class="award-item">
                        <div class="award-year">2023</div>
                        <div class="award-title">Инновация года в ритейле</div>
                        <div class="award-org">Retail Innovation Summit</div>
                    </div>
                    <div class="award-item">
                        <div class="award-year">2023</div>
                        <div class="award-title">Лидер роста</div>
                        <div class="award-org">Deloitte Technology Fast 500</div>
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>Готовы изменить свой бизнес?</h3>
                <p>Присоединяйтесь к тысячам успешных компаний, которые выбрали RetailNet Solutions</p>
                <a href="/become-partner/" class="btn btn-primary">Стать партнером</a>
                <a href="/contacts/" class="btn btn-outline-primary">Связаться с нами</a>
            </div>
            '''
        }
        return render(request, 'static_pages/about_company.html', context)


def it_integration(request):
    """IT-интеграция"""
    try:
        page = StaticPage.objects.get(slug='it-integration', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/it_integration.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Бесшовная IT-интеграция для вашего бизнеса',
            'content': '''
            <div class="hero-section">
                <h2>🔗 Объединяем все ваши системы в единую экосистему</h2>
                <p class="lead">Наши эксперты интегрируют ShopList с любыми корпоративными системами за 24-48 часов. Никаких простоев, только рост эффективности!</p>
            </div>
            
            <div class="integration-benefits">
                <h3>⚡ Почему интеграция критически важна</h3>
                <div class="benefits-grid">
                    <div class="benefit-card">
                        <div class="benefit-icon">📊</div>
                        <h4>Единая картина бизнеса</h4>
                        <p>Все данные в одном месте: продажи, склады, финансы, клиенты</p>
                        <div class="benefit-stat">+40% эффективности</div>
                    </div>
                    <div class="benefit-card">
                        <div class="benefit-icon">🤖</div>
                        <h4>Автоматизация процессов</h4>
                        <p>Исключаем ручной ввод данных и человеческие ошибки</p>
                        <div class="benefit-stat">-80% времени на рутину</div>
                    </div>
                    <div class="benefit-card">
                        <div class="benefit-icon">💰</div>
                        <h4>Снижение затрат</h4>
                        <p>Оптимизация процессов экономит до 30% операционных расходов</p>
                        <div class="benefit-stat">ROI 300% за год</div>
                    </div>
                </div>
            </div>
            
            <div class="integration-systems">
                <h3>🏗️ Системы, с которыми мы работаем</h3>
                
                <div class="systems-category">
                    <h4>💼 ERP-системы</h4>
                    <div class="systems-grid">
                        <div class="system-card featured">
                            <div class="system-logo">1️⃣</div>
                            <h5>1С:Предприятие</h5>
                            <p>Полная синхронизация товаров, остатков, цен и заказов</p>
                            <div class="integration-time">⏱️ Интеграция: 24 часа</div>
                            <div class="system-features">
                                <span class="feature">Автообмен</span>
                                <span class="feature">Реал-тайм</span>
                                <span class="feature">Двусторонний</span>
                            </div>
                        </div>
                        <div class="system-card">
                            <div class="system-logo">🔷</div>
                            <h5>SAP</h5>
                            <p>Интеграция с SAP ERP, S/4HANA</p>
                            <div class="integration-time">⏱️ Интеграция: 48 часов</div>
                        </div>
                        <div class="system-card">
                            <div class="system-logo">🔶</div>
                            <h5>Oracle ERP</h5>
                            <p>Подключение к Oracle Cloud ERP</p>
                            <div class="integration-time">⏱️ Интеграция: 72 часа</div>
                        </div>
                    </div>
                </div>
                
                <div class="systems-category">
                    <h4>👥 CRM-системы</h4>
                    <div class="systems-grid">
                        <div class="system-card">
                            <div class="system-logo">⚡</div>
                            <h5>Salesforce</h5>
                            <p>Синхронизация клиентов и истории покупок</p>
                        </div>
                        <div class="system-card">
                            <div class="system-logo">🎯</div>
                            <h5>amoCRM</h5>
                            <p>Автоматическое создание сделок из заказов</p>
                        </div>
                        <div class="system-card">
                            <div class="system-logo">🔧</div>
                            <h5>Битрикс24</h5>
                            <p>Полная интеграция с воронкой продаж</p>
                        </div>
                    </div>
                </div>
                
                <div class="systems-category">
                    <h4>💳 Платежные системы</h4>
                    <div class="systems-grid">
                        <div class="system-card">
                            <div class="system-logo">🏦</div>
                            <h5>Банковские API</h5>
                            <p>Сбербанк, ВТБ, Альфа-Банк, Тинькофф</p>
                        </div>
                        <div class="system-card">
                            <div class="system-logo">💰</div>
                            <h5>Платежные шлюзы</h5>
                            <p>Яндекс.Касса, CloudPayments, PayPal</p>
                        </div>
                        <div class="system-card">
                            <div class="system-logo">📱</div>
                            <h5>Мобильные платежи</h5>
                            <p>Apple Pay, Google Pay, Samsung Pay</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="integration-process">
                <h3>🚀 Как проходит интеграция</h3>
                <div class="process-timeline">
                    <div class="timeline-item">
                        <div class="timeline-number">1</div>
                        <div class="timeline-content">
                            <h4>Анализ и планирование</h4>
                            <p>Изучаем вашу IT-архитектуру и составляем план интеграции</p>
                            <div class="timeline-duration">1-2 дня</div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-number">2</div>
                        <div class="timeline-content">
                            <h4>Настройка подключений</h4>
                            <p>Создаем API-коннекторы и настраиваем обмен данными</p>
                            <div class="timeline-duration">1-3 дня</div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-number">3</div>
                        <div class="timeline-content">
                            <h4>Тестирование</h4>
                            <p>Проверяем корректность передачи данных на тестовой среде</p>
                            <div class="timeline-duration">1 день</div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-number">4</div>
                        <div class="timeline-content">
                            <h4>Запуск и поддержка</h4>
                            <p>Переводим интеграцию в продакшн и обеспечиваем поддержку</p>
                            <div class="timeline-duration">24/7</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="success-stories">
                <h3>📈 Истории успеха наших клиентов</h3>
                <div class="stories-grid">
                    <div class="story-card">
                        <div class="company-logo">🏪</div>
                        <h4>"Техносила"</h4>
                        <p>Интеграция с 1С увеличила скорость обработки заказов в 5 раз</p>
                        <div class="story-results">
                            <span class="result">+500% скорость</span>
                            <span class="result">-90% ошибок</span>
                        </div>
                    </div>
                    <div class="story-card">
                        <div class="company-logo">👔</div>
                        <h4>"Модный дом"</h4>
                        <p>Подключение CRM помогло увеличить повторные покупки на 40%</p>
                        <div class="story-results">
                            <span class="result">+40% retention</span>
                            <span class="result">+25% LTV</span>
                        </div>
                    </div>
                    <div class="story-card">
                        <div class="company-logo">🔧</div>
                        <h4>"ИнструментПро"</h4>
                        <p>Автоматизация складского учета сэкономила 20 часов в неделю</p>
                        <div class="story-results">
                            <span class="result">-20 часов/неделя</span>
                            <span class="result">+99% точность</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="pricing-section">
                <h3>💎 Тарифы на интеграцию</h3>
                <div class="pricing-grid">
                    <div class="pricing-card basic">
                        <h4>Базовая</h4>
                        <div class="price">от 50 000 ₽</div>
                        <ul>
                            <li>✅ 1 система интеграции</li>
                            <li>✅ Базовая настройка</li>
                            <li>✅ Техподдержка 3 месяца</li>
                            <li>✅ Документация</li>
                        </ul>
                        <button class="btn btn-outline-primary">Выбрать</button>
                    </div>
                    <div class="pricing-card premium">
                        <div class="pricing-badge">Популярный</div>
                        <h4>Профессиональная</h4>
                        <div class="price">от 150 000 ₽</div>
                        <ul>
                            <li>✅ До 3 систем интеграции</li>
                            <li>✅ Кастомная настройка</li>
                            <li>✅ Техподдержка 12 месяцев</li>
                            <li>✅ Обучение команды</li>
                            <li>✅ Мониторинг 24/7</li>
                        </ul>
                        <button class="btn btn-primary">Выбрать</button>
                    </div>
                    <div class="pricing-card enterprise">
                        <h4>Корпоративная</h4>
                        <div class="price">от 500 000 ₽</div>
                        <ul>
                            <li>✅ Неограниченные интеграции</li>
                            <li>✅ Персональный архитектор</li>
                            <li>✅ Пожизненная поддержка</li>
                            <li>✅ SLA 99.9%</li>
                            <li>✅ Приоритетная поддержка</li>
                        </ul>
                        <button class="btn btn-success">Обсудить</button>
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>Готовы интегрировать ваши системы?</h3>
                <p>Получите бесплатную консультацию архитектора и план интеграции за 24 часа</p>
                <a href="/contacts/" class="btn btn-primary">Получить консультацию</a>
                <a href="#" class="btn btn-outline-primary">Скачать кейсы</a>
            </div>
            '''
        }
        return render(request, 'static_pages/it_integration.html', context)


def retail_networks(request):
    """Розничные сети"""
    try:
        page = StaticPage.objects.get(slug='retail-networks', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/retail_networks.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Розничные сети',
            'content': '''
            <h2>Решения для розничных сетей</h2>
            <p>Специализированные решения для управления розничными сетями:</p>
            <ul>
                <li><strong>Централизованное управление</strong> - единая система для всех точек продаж</li>
                <li><strong>Аналитика и отчетность</strong> - детальная статистика по каждому магазину</li>
                <li><strong>Управление ассортиментом</strong> - автоматическое распределение товаров</li>
                <li><strong>Контроль цен</strong> - единая ценовая политика по всей сети</li>
                <li><strong>Программы лояльности</strong> - бонусные системы для покупателей</li>
            </ul>
            '''
        }
        return render(request, 'static_pages/retail_networks.html', context)


def for_stores(request):
    """Для магазинов"""
    try:
        page = StaticPage.objects.get(slug='for-stores', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/for_stores.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Для магазинов',
            'content': '''
            <h2>Возможности для магазинов</h2>
            <p>Присоединяйтесь к нашей платформе и получите доступ к:</p>
            <div class="features-list">
                <div class="feature">
                    <h3><i class="fas fa-store"></i> Витрина товаров</h3>
                    <p>Создайте привлекательную витрину своих товаров</p>
                </div>
                <div class="feature">
                    <h3><i class="fas fa-chart-line"></i> Аналитика продаж</h3>
                    <p>Отслеживайте продажи и анализируйте спрос</p>
                </div>
                <div class="feature">
                    <h3><i class="fas fa-users"></i> База клиентов</h3>
                    <p>Работайте с постоянными покупателями</p>
                </div>
                <div class="feature">
                    <h3><i class="fas fa-shipping-fast"></i> Доставка</h3>
                    <p>Интеграция со службами доставки</p>
                </div>
            </div>
            '''
        }
        return render(request, 'static_pages/for_stores.html', context)


def add_products(request):
    """Добавить товары"""
    try:
        page = StaticPage.objects.get(slug='add-products', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/add_products.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Добавить товары',
            'content': '''
            <h2>Как добавить товары</h2>
            <p>Для добавления товаров на платформу выполните следующие шаги:</p>
            <ol>
                <li><strong>Зарегистрируйтесь</strong> как продавец на нашей платформе</li>
                <li><strong>Подтвердите</strong> свои документы и реквизиты</li>
                <li><strong>Загрузите товары</strong> через личный кабинет или API</li>
                <li><strong>Настройте цены</strong> и условия доставки</li>
                <li><strong>Опубликуйте</strong> товары после модерации</li>
            </ol>
            <div class="cta-section">
                <h3>Готовы начать?</h3>
                <a href="#" class="btn btn-primary">Зарегистрироваться как продавец</a>
            </div>
            '''
        }
        return render(request, 'static_pages/add_products.html', context)


def manage_assortment(request):
    """Управление ассортиментом"""
    try:
        page = StaticPage.objects.get(slug='manage-assortment', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/manage_assortment.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Управление ассортиментом',
            'content': '''
            <h2>Управление ассортиментом</h2>
            <p>Эффективные инструменты для управления товарным ассортиментом:</p>
            <div class="tools-grid">
                <div class="tool">
                    <h3>Массовые операции</h3>
                    <p>Изменяйте цены и характеристики сразу для множества товаров</p>
                </div>
                <div class="tool">
                    <h3>Автоматические правила</h3>
                    <p>Настройте автоматическое управление ценами и наличием</p>
                </div>
                <div class="tool">
                    <h3>Импорт/экспорт</h3>
                    <p>Загружайте товары из Excel или выгружайте отчеты</p>
                </div>
                <div class="tool">
                    <h3>Аналитика</h3>
                    <p>Анализируйте эффективность товаров и категорий</p>
                </div>
            </div>
            '''
        }
        return render(request, 'static_pages/manage_assortment.html', context)


def become_partner(request):
    """Стать партнером"""
    try:
        page = StaticPage.objects.get(slug='become-partner', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/become_partner.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Стать партнером',
            'content': '''
            <h2>Партнерская программа</h2>
            <p>Присоединяйтесь к нашей партнерской программе и получайте выгоду:</p>
            <div class="benefits">
                <div class="benefit">
                    <h3>Комиссия до 15%</h3>
                    <p>Получайте процент с каждой продажи</p>
                </div>
                <div class="benefit">
                    <h3>Маркетинговая поддержка</h3>
                    <p>Рекламные материалы и промо-акции</p>
                </div>
                <div class="benefit">
                    <h3>Персональный менеджер</h3>
                    <p>Индивидуальная поддержка и консультации</p>
                </div>
            </div>
            <div class="partner-form">
                <h3>Заявка на партнерство</h3>
                <p>Заполните форму, и мы свяжемся с вами в течение 24 часов:</p>
                <a href="#" class="btn btn-success">Подать заявку</a>
            </div>
            '''
        }
        return render(request, 'static_pages/become_partner.html', context)


def support(request):
    """Поддержка"""
    try:
        page = StaticPage.objects.get(slug='support', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/support.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'Поддержка мирового уровня 24/7',
            'content': '''
            <div class="hero-section">
                <h2>🎧 Мы здесь, чтобы помочь вам!</h2>
                <p class="lead">Наша команда из 150+ экспертов готова решить любой вопрос за считанные минуты. Средний рейтинг поддержки: 4.9/5 ⭐</p>
            </div>
            
            <div class="support-stats">
                <div class="stats-showcase">
                    <div class="stat-item">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-value">30 сек</div>
                        <div class="stat-label">Среднее время ответа</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-value">98%</div>
                        <div class="stat-label">Решение с первого раза</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-icon">🌍</div>
                        <div class="stat-value">24/7</div>
                        <div class="stat-label">Поддержка без выходных</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-icon">💬</div>
                        <div class="stat-value">12</div>
                        <div class="stat-label">Языков поддержки</div>
                    </div>
                </div>
            </div>
            
            <div class="support-channels">
                <h3>🚀 Выберите удобный способ связи</h3>
                <div class="channels-grid">
                    <div class="channel-card instant">
                        <div class="channel-badge">Мгновенно</div>
                        <div class="channel-icon">💬</div>
                        <h4>Живой чат</h4>
                        <p>Общайтесь с экспертами в реальном времени</p>
                        <div class="channel-stats">
                            <span class="stat">⚡ 15 сек ответ</span>
                            <span class="stat">👥 50+ консультантов онлайн</span>
                        </div>
                        <button class="btn btn-primary">Начать чат</button>
                    </div>
                    
                    <div class="channel-card">
                        <div class="channel-icon">📱</div>
                        <h4>WhatsApp/Telegram</h4>
                        <p>Пишите в любое время - отвечаем быстро</p>
                        <div class="channel-stats">
                            <span class="stat">⚡ 2 мин ответ</span>
                            <span class="stat">📸 Можно отправлять фото</span>
                        </div>
                        <div class="messenger-buttons">
                            <a href="#" class="btn btn-success">WhatsApp</a>
                            <a href="#" class="btn btn-info">Telegram</a>
                        </div>
                    </div>
                    
                    <div class="channel-card">
                        <div class="channel-icon">📞</div>
                        <h4>Горячая линия</h4>
                        <p>Бесплатные звонки по России</p>
                        <div class="hotline-number">8 (800) 234-56-78</div>
                        <div class="channel-stats">
                            <span class="stat">🆓 Звонки бесплатно</span>
                            <span class="stat">🎧 Без очередей</span>
                        </div>
                    </div>
                    
                    <div class="channel-card">
                        <div class="channel-icon">📧</div>
                        <h4>Email поддержка</h4>
                        <p>Подробные ответы на сложные вопросы</p>
                        <div class="email-address">support@shoplist.ru</div>
                        <div class="channel-stats">
                            <span class="stat">⏰ Ответ в течение часа</span>
                            <span class="stat">📎 Можно прикреплять файлы</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="support-categories">
                <h3>🎯 Специализированная помощь</h3>
                <div class="categories-grid">
                    <div class="category-card">
                        <div class="category-icon">🛒</div>
                        <h4>Помощь с заказами</h4>
                        <ul>
                            <li>Оформление и изменение заказов</li>
                            <li>Отслеживание доставки</li>
                            <li>Возвраты и обмены</li>
                            <li>Проблемы с оплатой</li>
                        </ul>
                        <button class="btn btn-outline-primary">Получить помощь</button>
                    </div>
                    
                    <div class="category-card">
                        <div class="category-icon">🔧</div>
                        <h4>Техническая поддержка</h4>
                        <ul>
                            <li>Проблемы с сайтом/приложением</li>
                            <li>Настройка аккаунта</li>
                            <li>API и интеграции</li>
                            <li>Безопасность данных</li>
                        </ul>
                        <button class="btn btn-outline-primary">Техподдержка</button>
                    </div>
                    
                    <div class="category-card">
                        <div class="category-icon">💼</div>
                        <h4>Бизнес-поддержка</h4>
                        <ul>
                            <li>Настройка магазина</li>
                            <li>Консультации по продажам</li>
                            <li>Аналитика и отчеты</li>
                            <li>Маркетинговые инструменты</li>
                        </ul>
                        <button class="btn btn-outline-primary">Бизнес-консультация</button>
                    </div>
                    
                    <div class="category-card">
                        <div class="category-icon">🎓</div>
                        <h4>Обучение и консультации</h4>
                        <ul>
                            <li>Вебинары и мастер-классы</li>
                            <li>Персональное обучение</li>
                            <li>Лучшие практики</li>
                            <li>Сертификация</li>
                        </ul>
                        <button class="btn btn-outline-primary">Записаться на обучение</button>
                    </div>
                </div>
            </div>
            
            <div class="self-service">
                <h3>🔍 Центр самообслуживания</h3>
                <div class="self-service-grid">
                    <div class="service-item">
                        <div class="service-icon">📚</div>
                        <h4>База знаний</h4>
                        <p>1000+ статей и инструкций</p>
                        <div class="service-stats">
                            <span class="popular-tag">🔥 Популярное</span>
                            <span class="updated-tag">🆕 Обновляется ежедневно</span>
                        </div>
                        <button class="btn btn-outline-primary">Открыть базу знаний</button>
                    </div>
                    
                    <div class="service-item">
                        <div class="service-icon">❓</div>
                        <h4>FAQ</h4>
                        <p>Ответы на частые вопросы</p>
                        <div class="service-stats">
                            <span class="popular-tag">⚡ Быстрые ответы</span>
                            <span class="updated-tag">🎯 95% покрытие вопросов</span>
                        </div>
                        <button class="btn btn-outline-primary">Посмотреть FAQ</button>
                    </div>
                    
                    <div class="service-item">
                        <div class="service-icon">🎥</div>
                        <h4>Видеоуроки</h4>
                        <p>Пошаговые инструкции</p>
                        <div class="service-stats">
                            <span class="popular-tag">📺 200+ видео</span>
                            <span class="updated-tag">🎬 HD качество</span>
                        </div>
                        <button class="btn btn-outline-primary">Смотреть видео</button>
                    </div>
                    
                    <div class="service-item">
                        <div class="service-icon">🤖</div>
                        <h4>ИИ-помощник</h4>
                        <p>Умный бот для быстрых ответов</p>
                        <div class="service-stats">
                            <span class="popular-tag">🧠 Понимает контекст</span>
                            <span class="updated-tag">⚡ Мгновенные ответы</span>
                        </div>
                        <button class="btn btn-outline-primary">Спросить бота</button>
                    </div>
                </div>
            </div>
            
            <div class="premium-support">
                <h3>👑 Премиум поддержка</h3>
                <div class="premium-features">
                    <div class="premium-card">
                        <div class="premium-badge">VIP</div>
                        <h4>Персональный менеджер</h4>
                        <p>Выделенный эксперт для вашего бизнеса</p>
                        <ul>
                            <li>✅ Прямая линия связи</li>
                            <li>✅ Приоритетная поддержка</li>
                            <li>✅ Еженедельные отчеты</li>
                            <li>✅ Стратегические консультации</li>
                        </ul>
                        <div class="premium-price">от 50 000 ₽/мес</div>
                        <button class="btn btn-success">Подключить VIP</button>
                    </div>
                    
                    <div class="premium-card">
                        <div class="premium-badge">Enterprise</div>
                        <h4>Корпоративная поддержка</h4>
                        <p>Комплексное сопровождение крупного бизнеса</p>
                        <ul>
                            <li>✅ Команда экспертов</li>
                            <li>✅ SLA 99.9%</li>
                            <li>✅ Круглосуточная поддержка</li>
                            <li>✅ Выделенная инфраструктура</li>
                        </ul>
                        <div class="premium-price">Индивидуально</div>
                        <button class="btn btn-primary">Обсудить условия</button>
                    </div>
                </div>
            </div>
            
            <div class="feedback-section">
                <h3>⭐ Оцените нашу поддержку</h3>
                <div class="feedback-stats">
                    <div class="rating-display">
                        <div class="rating-stars">⭐⭐⭐⭐⭐</div>
                        <div class="rating-score">4.9/5</div>
                        <div class="rating-count">на основе 50,000+ отзывов</div>
                    </div>
                    <div class="recent-reviews">
                        <div class="review-item">
                            <div class="review-stars">⭐⭐⭐⭐⭐</div>
                            <p>"Решили проблему за 2 минуты! Супер!"</p>
                            <div class="review-author">- Анна К.</div>
                        </div>
                        <div class="review-item">
                            <div class="review-stars">⭐⭐⭐⭐⭐</div>
                            <p>"Лучшая поддержка, что я видел"</p>
                            <div class="review-author">- Михаил Р.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>Нужна помощь прямо сейчас?</h3>
                <p>Не тратьте время на поиски - наши эксперты уже готовы помочь!</p>
                <a href="#" class="btn btn-primary">Начать чат</a>
                <a href="tel:88002345678" class="btn btn-outline-primary">Позвонить</a>
            </div>
            '''
        }
        return render(request, 'static_pages/support.html', context)


def retailnet_solutions(request):
    """RetailNet Solutions"""
    try:
        page = StaticPage.objects.get(slug='retailnet-solutions', is_active=True)
        context = {'page': page}
        return render(request, 'static_pages/retailnet_solutions.html', context)
    except StaticPage.DoesNotExist:
        context = {
            'title': 'RetailNet Solutions',
            'content': '''
            <h2>RetailNet Solutions</h2>
            <p>Комплексные IT-решения для розничной торговли и e-commerce:</p>
            <div class="solutions-grid">
                <div class="solution">
                    <h3>E-commerce платформы</h3>
                    <p>Создание интернет-магазинов и маркетплейсов</p>
                </div>
                <div class="solution">
                    <h3>Мобильные приложения</h3>
                    <p>Разработка iOS и Android приложений</p>
                </div>
                <div class="solution">
                    <h3>Системы лояльности</h3>
                    <p>Программы бонусов и скидок для клиентов</p>
                </div>
                <div class="solution">
                    <h3>Аналитика и BI</h3>
                    <p>Системы бизнес-аналитики и отчетности</p>
                </div>
                <div class="solution">
                    <h3>Интеграции</h3>
                    <p>Подключение к внешним сервисам и API</p>
                </div>
                <div class="solution">
                    <h3>Облачные решения</h3>
                    <p>Миграция в облако и DevOps</p>
                </div>
            </div>
            '''
        }
        return render(request, 'static_pages/retailnet_solutions.html', context)