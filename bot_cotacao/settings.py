BOT_NAME = "bot_cotacao"

SPIDER_MODULES = ["bot_cotacao.spiders"]
NEWSPIDER_MODULE = "bot_cotacao.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 20

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     "bot_cotacao.middlewares.BotCotacaoSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "bot_cotacao.middlewares.BotCotacaoDownloaderMiddleware": 543,
# }

DOWNLOADER_MIDDLEWARES = {
    "bot_cotacao.middlewares.BotCotacaoDownloaderMiddleware": 120,
    'bot_cotacao.middlewares.RandomUserAgentMiddleware': 200,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 250,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 320,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,

}


FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
]

USER_AGENT = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) ' \
             r'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 ' \
             r'Safari/537.36'

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "bot_cotacao.pipelines.BotCotacaoPipeline": 300,
    "bot_cotacao.pipelines.ImagesPipelineProduct": 350
}

IMAGES_STORE = './images/'
RETRY_ENABLED = True
RETRY_TIMES = 10  # tenta até 10 vezes antes de desistir
RETRY_DELAY = 10  # espera 10 segundos entre cada tentativa
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# SPLASH CONFIGURATIONS

SPLASH_URL = 'http://localhost:8050'  # Endereço do Splash
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'  # Classe de filtro de duplicatas para o Splash
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'  # Armazenamento em cache do Splash

# SPIDER_MIDDLEWARES = {  # Middlewares de aranha do Splash
#     'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
# }

# Configurações do proxy SOCKS5
# SOCKS5_PROXY_HOST = 'localhost'  # Endereço do Tor
# SOCKS5_PROXY_PORT = 9050  # Porta do Tor
# SOCKS5_PROXY_USERNAME = None  # Nome de usuário (opcional)
# SOCKS5_PROXY_PASSWORD = None  # Senha (opcional)
