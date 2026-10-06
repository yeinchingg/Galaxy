const WIKI_URL_MAP = {
  // 🪐 太陽系相關 (ID 1 ~ 22)
  "https://openstax.org/l/30proprorx": {
    id: "ID 1",
    title: "太陽 (The Sun)",
    description:
      "太陽為太陽系中心的 G2V 型主序星，佔太陽系總質量 99.8% 以上[cite: 1]。核心溫度達 1500 萬 K，透過質子－質子鏈反應將氫融合成氦並釋放巨大能量[cite: 1]。大氣層由內而外分為光球層、色球層與日冕[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 15 章與第 16 章[cite: 1]",
      "維基百科「太陽」條目[cite: 1]",
      "NASA Science 網站[cite: 1]",
    ],
    relatedTopicName: "質子－質子鏈反應[cite: 1]",
  },
  "https://openstax.org/l/30NASAVehicle": {
    id: "ID 1 / ID 22",
    title: "太陽 / 日球層頂 / 太陽圈 (Heliopause)",
    description:
      "由太陽風向外吹送高能等離子體形成的氣泡狀區域[cite: 1]，當太陽風壓力與星際介質達到平衡時的交界面稱為日球層頂[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 15 章[cite: 1]",
      "維基百科「日球層頂」條目[cite: 1]",
    ],
    relatedTopicName: "日冕與帕克太陽探測器 / 航海家 1 號穿越日球層頂[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E8%90%AC%E6%9C%89%E5%BC%95%E5%8A%9B%E5%AE%9A%E5%BE%8B":
    {
      id: "ID 2",
      title: "水星 (Mercury)",
      description:
        "離太陽最近的類地行星，軌道半長軸約 0.39 AU[cite: 1]，公轉週期僅 88 地球日[cite: 1]，平均軌道速度約 48 km/s[cite: 1]，為太陽系移動最快的行星[cite: 1]。無大氣層與天然衛星[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 3 章[cite: 1]",
        "維基百科「水星」與「太陽系」條目[cite: 1]",
      ],
      relatedTopicName: "克卜勒軌道參數與水星近日點進動[cite: 1]",
    },
  "https://openstax.org/l/30VenusandSun": {
    id: "ID 3",
    title: "金星 (Venus)",
    description:
      "距離太陽約 0.72 AU 的類地行星[cite: 1]。擁有濃密且富含二氧化碳的大氣層，引發強烈溫室效應，表面溫度超過 460 °C[cite: 1]，為夜空除月球外最亮天體[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章與第 17 章[cite: 1]",
      "維基百科「金星」條目[cite: 1]",
    ],
    relatedTopicName: "金星凌日測量天文單位[cite: 1]",
  },
  "https://openstax.org/l/30Aurora": {
    id: "ID 4",
    title: "地球 (Earth)",
    description:
      "距離太陽約 1 AU，已知唯一存在生命的天體[cite: 1]。擁有液態水海洋、氮氧大氣層，以及由液態外核電流產生的地磁場，能阻擋高能帶電粒子[cite: 1]。",
    sources: [
      "NASA Science「Four Forces」專題[cite: 1]",
      "維基百科「地球」條目[cite: 1]",
    ],
    relatedTopicName: "地球磁場與極光效應[cite: 1]",
  },
  "https://openstax.org/l/30parallaxmod": {
    id: "ID 5 / ID 43",
    title: "月球 / 北極星 (Polaris)",
    description:
      "地球唯一的天然衛星，其潮汐力引發地球海洋漲退潮[cite: 1]。古人曾利用其與地球直徑作為三角測量基線估算天體距離[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「月球」條目[cite: 1]",
    ],
    relatedTopicName: "視差與三角測量法 / 歲差與北極星演變[cite: 1]",
  },
  "https://science.nasa.gov/universe/stars/": {
    id: "ID 6 / ID 16",
    title: "火星 / 木衛一 伊奧與木衛四 卡利斯多 (Io & Callisto)",
    description:
      "第四顆類地行星（1.52 AU），公轉週期 1.88 地球年[cite: 1]。大氣稀薄，表面覆蓋氧化鐵沙塵呈紅色，古地貌顯示數十億年前曾有液態水[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章與第 30 章[cite: 1]",
      "維基百科「火星」條目[cite: 1]",
    ],
    relatedTopicName: "火星表面液態水與探測任務 / 木星潮汐加熱機制[cite: 1]",
  },
  "https://openstax.org/l/30cirhabzonsim": {
    id: "ID 7 / ID 15",
    title: "木星 / 木衛二 歐羅巴 (Europa)",
    description:
      "太陽系體積與質量最大的氣態巨行星（質量為地球 318 倍）[cite: 1]。主要由氫和氦組成，與土星合佔非太陽質量的近 90%[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章[cite: 1]",
      "維基百科「木星」條目[cite: 1]",
    ],
    relatedTopicName: "伽利略衛星系統 / 木衛二地下海洋與外星生命探測[cite: 1]",
  },
  "https://openstax.org/l/30wohooceins": {
    id: "ID 8",
    title: "土星 (Saturn)",
    description:
      "距離太陽第六近的氣態巨行星，擁有寬廣明亮的冰質行星環系統[cite: 1]。平均密度小於水，主要成分為氫與氦[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章[cite: 1]",
      "維基百科「土星」條目[cite: 1]",
    ],
    relatedTopicName: "卡西尼號探測土星與土衛系統[cite: 1]",
  },
  "https://science.nasa.gov/universe/galaxies/": {
    id: "ID 9",
    title: "天王星 (Uranus)",
    description:
      "第七顆行星（冰巨行星），1781 年由威廉·赫歇爾發現[cite: 1]。大氣含水、氨、甲烷等「冰」成分，自轉軸極度傾斜[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章[cite: 1]",
      "維基百科「天王星」條目[cite: 1]",
    ],
    relatedTopicName: "太陽系冰巨行星大氣結構[cite: 1]",
  },
  "https://openstax.org/l/30nepplumatdis": {
    id: "ID 10",
    title: "海王星 (Neptune)",
    description:
      "最外圍八大行星（約 30 AU），1846 年由加勒根據亞當斯與勒維耶的重力攝動計算預測位置後發現，為天體力學重大勝利[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章 第 6 節[cite: 1]",
      "維基百科「海王星」條目[cite: 1]",
    ],
    relatedTopicName: "海王星的數學預測與發現歷史[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%A9%E9%AB%94%E5%88%97%E8%A1%A8":
    {
      id: "ID 11 / ID 14 / ID 20 / ID 21",
      title: "穀神星 / 妊神星與鳥神星 / 柯伊伯帶 / 歐特雲",
      description:
        "小行星帶中最大的天體（2.77 AU），2006 年歸類為矮行星，是小行星帶中唯一呈球形（流體靜力平衡）的天體[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 3 章[cite: 1]",
        "維基百科「穀神星」與「矮行星」條目[cite: 1]",
      ],
      relatedTopicName:
        "小行星帶與矮行星分類 / 柯伊伯帶天體 (KBO) / 短週期彗星與柯伊伯帶 / 長週期彗星起源[cite: 1]",
    },
  "https://openstax.org/l/30DistanceScale": {
    id: "ID 12",
    title: "冥王星 (Pluto)",
    description:
      "位於柯伊伯帶的冰質矮行星，軌道傾角 17°[cite: 1]。2006 年前為九大行星之一，後因未能清空軌道周圍天體而改分類為矮行星[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章[cite: 1]",
      "維基百科「冥王星」條目[cite: 1]",
    ],
    relatedTopicName: "柯伊伯帶天體與新視野號任務[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%99%BD%E7%B3%BB": {
    id: "ID 13 / ID 19",
    title: "鬩神星 / 小行星帶 (Asteroid Belt)",
    description:
      "位於柯伊伯帶外圍的巨大矮行星，軌道傾角達 44°[cite: 1]。其發現促使天文學家重新定義行星標準[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「鬩神星」條目[cite: 1]",
    ],
    relatedTopicName:
      "國際天文聯合會 (IAU) 行星定義 / 太陽系形成與原行星盤雪線[cite: 1]",
  },
  "https://openstax.org/l/30huytatsurf": {
    id: "ID 17",
    title: "土衛六 泰坦 (Titan)",
    description:
      "土星最大衛星，擁有比地球濃密的氮氣大氣層，表面存在液態甲烷與乙烷構成的河流、湖泊與沙丘[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 30 章[cite: 1]",
      "維基百科「土衛六」條目[cite: 1]",
    ],
    relatedTopicName: "惠更斯號探測土衛六表面[cite: 1]",
  },
  "https://www.youtube.com/watch?v=KzVxqmYu90Y": {
    id: "ID 18",
    title: "土衛二 恩克拉多斯 (Enceladus)",
    description:
      "土星冰質小衛星，南極區域有巨型冰噴泉（羽流），將冰殼下液態海洋物質噴射至太空[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 30 章[cite: 1]",
      "維基百科「土衛二」條目[cite: 1]",
    ],
    relatedTopicName: "卡西尼號發現土衛二冰噴泉[cite: 1]",
  },

  // ⚡ 恆星演化與特定恆星 (ID 23 ~ 46)
  "https://openstax.org/l/30spectexpl": {
    id: "ID 23",
    title: "恆星 (Star)",
    description:
      "由高溫氣體組成、藉由核心核融合反應抵抗自身重力塌縮的巨大發光球體，為星系基本組成單位[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 17 章[cite: 1]",
      "NASA Science「Stars」專題[cite: 1]",
      "維基百科「恆星」條目[cite: 1]",
    ],
    relatedTopicName: "恆星光譜與光度分類[cite: 1]",
  },
  "https://openstax.org/l/30aniomelen": {
    id: "ID 24",
    title: "原恆星 (Protostar)",
    description:
      "分子雲團塊在自身重力下塌縮生熱，尚未點燃核心氫融合反應之前的恆星胚胎階段[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 21 章[cite: 1]",
      "維基百科「恆星演化」條目[cite: 1]",
    ],
    relatedTopicName: "原恆星演化軌跡與赫羅圖[cite: 1]",
  },
  "https://openstax.org/l/30starmass": {
    id: "ID 25",
    title: "主序星 (Main-Sequence Star)",
    description:
      "恆星一生中最漫長且穩定的時期（約佔生命的 90%），核心穩定進行氫融合為氦的反應[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 18 章與第 22 章[cite: 1]",
      "維基百科「主序星」條目[cite: 1]",
    ],
    relatedTopicName: "主序星質量－光度關係[cite: 1]",
  },
  "https://openstax.org/l/30starinbox": {
    id: "ID 26 / ID 27",
    title: "次巨星 / 紅巨星 / 巨星",
    description:
      "核心氫燃料耗盡後，恆星離開主序帶、外層大氣開始膨脹且光度上升的過渡階段[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 22 章[cite: 1]",
      "維基百科「恆星演化」與「紅巨星」條目[cite: 1]",
    ],
    relatedTopicName: "次巨星分支與殼層氫融合 / 三氦過程與氦閃[cite: 1]",
  },
  "https://science.nasa.gov/universe/what-is-betelgeuse-inside-the-strange-volatile-star/":
    {
      id: "ID 28 / ID 42",
      title: "紅超巨星 / 參宿四與參宿七",
      description:
        "大質量恆星演化晚期的極度膨脹狀態，半徑可達數個 AU，核心能進行多重元素融合直到生成鐵[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 22 章[cite: 1]",
        "維基百科「超巨星」條目[cite: 1]",
      ],
      relatedTopicName: "參宿四紅超巨星結構 / 參宿四的大減光現象[cite: 1]",
    },
  "https://openstax.org/l/30hubimgwhidwa": {
    id: "ID 29 / ID 110",
    title: "白矮星 / 電子簡併壓與錢德拉塞卡極限",
    description:
      "中低質量恆星拋散外層後留下的高密度核心殘骸，依靠電子簡併壓抗衡重力[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 23 章[cite: 1]",
      "維基百科「白矮星」條目[cite: 1]",
    ],
    relatedTopicName:
      "錢德拉塞卡極限與電子簡併壓 / 錢德拉塞卡諾貝爾獎研究與白矮星演化[cite: 1]",
  },
  "https://openstax.org/l/30diamondstar": {
    id: "ID 30",
    title: "黑矮星 (Black Dwarf)",
    description:
      "白矮星將內部殘餘熱能輻射殆盡後，不再發光冷卻形成的最終冷卻天體殘骸[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 23 章[cite: 1]",
      "維基百科「黑矮星」條目[cite: 1]",
    ],
    relatedTopicName: "白矮星冷卻與晶體化[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E7%B7%BB%E5%AF%86%E6%98%9F": {
    id: "ID 31 / ID 111",
    title: "中子星 / 中子簡併壓 (Neutron Degeneracy Pressure)",
    description:
      "大質量恆星超新星爆炸後形成的極高密度殘骸（直徑約 20 公里），依靠中子簡併壓對抗重力[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 23 章[cite: 1]",
      "維基百科「中子星」條目[cite: 1]",
    ],
    relatedTopicName:
      "托爾曼—奧本海默—沃爾科夫極限 / 托爾曼—奧本海默—沃爾科夫 (TOV) 極限[cite: 1]",
  },
  "https://openstax.org/l/30jocbellint": {
    id: "ID 32",
    title: "脈衝星 (Pulsar)",
    description:
      "高速自轉且具備強烈磁場的中子星，向外發出週期性電波與磁場脈衝訊號[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 23 章 第 4 節[cite: 1]",
      "維基百科「脈衝星」條目[cite: 1]",
    ],
    relatedTopicName: "燈塔模型與賈絲琳·貝爾的發現[cite: 1]",
  },
  "http://solomon.as.utexas.edu/magnetar.html": {
    id: "ID 33",
    title: "磁星 (Magnetar)",
    description:
      "擁有超強磁場（比地球強數百兆倍）的中子星，外殼破裂引發星震時會釋放巨大 X 射線與伽瑪射線暴發[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 23 章[cite: 1]",
      "維基百科「磁星」條目[cite: 1]",
    ],
    relatedTopicName: "星震與 SGR 1806-20 暴發事件[cite: 1]",
  },
  "https://www.space.com/23798-brown-dwarfs.html": {
    id: "ID 34",
    title: "棕矮星 (Brown Dwarf)",
    description:
      "質量介於最大氣態行星與最小恆星之間（約 13～80 木星質量）的天體，核心不足以點燃穩定的氫融合[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 17 章[cite: 1]",
      "維基百科「棕矮星」條目[cite: 1]",
    ],
    relatedTopicName: "氘融合臨界與 L/T/Y 光譜型[cite: 1]",
  },
  "https://openstax.org/l/30HerbigHaro1": {
    id: "ID 35",
    title: "T 金牛座型星 (T Tauri Star)",
    description:
      "中低質量原恆星即將進入主序帶之前的演化階段，展現強烈恆星風、吸積盤與強烈光譜變異[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 21 章[cite: 1]",
      "維基百科「T 金牛座型星」條目[cite: 1]",
    ],
    relatedTopicName: "原恆星噴流與 Herbig-Haro 天體[cite: 1]",
  },
  "https://openstax.org/l/30sloandigsky": {
    id: "ID 36",
    title: "造父變星 (Cepheid Variables)",
    description:
      "脈動週期與真實光度成正比的黃色超巨星，為量測河外星系距離的核心標準燭光[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「造父變星」條目[cite: 1]",
    ],
    relatedTopicName: "亨麗埃塔·勒維特與週期－光度關係[cite: 1]",
  },
  "https://www.aavso.org/": {
    id: "ID 37",
    title: "RR 琴座型變星 (RR Lyrae Variables)",
    description:
      "週期小於 1 天的年老脈動巨星，絕對光度近似常數，常用於測量銀河系內及球狀星團距離[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「RR 琴座型變星」條目[cite: 1]",
    ],
    relatedTopicName: "球狀星團距離量測[cite: 1]",
  },
  "https://exoplanets.nasa.gov/": {
    id: "ID 38 / ID 307",
    title: "比鄰星 / 開普勒太空望遠鏡與 TESS 衛星",
    description:
      "距離太陽系最近的恆星（約 4.25 光年），屬於 M 型低光度紅矮星，已知擁有系外行星[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「比鄰星」條目[cite: 1]",
    ],
    relatedTopicName:
      "Proxima b 宜居帶系外行星 / NASA Exoplanet Exploration 巡天數據庫[cite: 1]",
  },
  "https://www.planetary.org/worlds/exoplanets": {
    id: "ID 39",
    title: "半人馬座 α 星 (Alpha Centauri A/B)",
    description:
      "距離太陽系最近的聯星系統（約 4.4 光年），包含類似太陽的 G 型星 A 與 K 型星 B[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「半人馬座α」條目[cite: 1]",
    ],
    relatedTopicName: "Breakthrough Starshot 突破攝星計畫[cite: 1]",
  },
  "https://hubblesite.org/contents/news-releases/2005/news-2005-36.html": {
    id: "ID 40",
    title: "天狼星 A 與天狼星 B",
    description:
      "天狼星 A 為全天肉眼最亮主序星；天狼星 B 為人類歷史上記錄的第一顆白矮星伴星[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 18 章[cite: 1]",
      "維基百科「天狼星」條目[cite: 1]",
    ],
    relatedTopicName: "哈伯望遠鏡與錢卓拉望遠鏡觀測天狼星 B[cite: 1]",
  },
  "https://zh.wikipedia.org/wiki/%E6%81%86%E6%98%9F": {
    id: "ID 41",
    title: "織女星與牛郎星",
    description:
      "織女星為琴座 A 型主序星，視星等曾經定義為 0；牛郎星為天鷹座高速自轉星，兩者皆為夏季大三角成員[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 17 章[cite: 1]",
      "維基百科「織女一」與「牽牛星」條目[cite: 1]",
    ],
    relatedTopicName: "夏季大三角與民間傳說[cite: 1]",
  },
  "https://openstax.org/l/30spectconst": {
    id: "ID 44",
    title: "巴納德星 (Barnard's Star)",
    description:
      "全天已知自行速度最大的恆星（每年 10.3 角秒），距離地球約 6 光年的低質量紅矮星[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 20 章[cite: 1]",
      "維基百科「巴納德星」條目[cite: 1]",
    ],
    relatedTopicName: "恆星自行與空間速度向量[cite: 1]",
  },
  "https://earthsky.org/brightest-stars/algol-the-demon-star/": {
    id: "ID 45",
    title: "大陵五 / 惡魔星 (Algol)",
    description:
      "英仙座最著名的食雙星，亮度會週期性因為兩星相互遮擋而發生食變[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 18 章[cite: 1]",
      "維基百科「大陵五」條目[cite: 1]",
    ],
    relatedTopicName: "食雙星光度曲線與大陵五悖論[cite: 1]",
  },
  "https://esahubble.org/images/archive/category/nebulae": {
    id: "ID 46 / ID 71",
    title: "心宿二 / 發射星雲 / H II 區 (Emission Nebula)",
    description:
      "天蠍座核心的紅超巨星，周圍環繞著自身拋射物質組成的黃紅色反射塵埃雲[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 20 章[cite: 1]",
      "維基百科「心宿二」條目[cite: 1]",
    ],
    relatedTopicName: "反射星雲與星際塵埃 / H II 區與電離氫光譜[cite: 1]",
  },

  // 🌌 星系、黑洞、星雲 (ID 47 ~ 78)
  "https://openstax.org/l/30gaiastars": {
    id: "ID 47",
    title: "銀河系 (Milky Way Galaxy)",
    description:
      "我們太陽系所在的棒旋星系，直徑超過 10 萬光年，包含 2000 億～4000 億顆恆星，中心擁有超大質量黑洞人馬座 A*[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 25 章[cite: 1]",
      "NASA Science「Galaxies」專題[cite: 1]",
      "維基百科「銀河系」條目[cite: 1]",
    ],
    relatedTopicName: "銀河系結構與 Gaia 三維星圖[cite: 1]",
  },
  "https://openstax.org/l/30galaxphohubb": {
    id: "ID 48 / ID 49 / ID 50 / ID 52",
    title: "螺旋星系 / 橢圓星系 / 不規則星系 / 仙女座星系 (Andromeda / M31)",
    description:
      "具有中央核球、扁平星盤與旋臂結構的星系，旋臂中富含氣體與塵埃，新恆星形成活躍[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 26 章[cite: 1]",
      "維基百科「螺旋星系」條目[cite: 1]",
    ],
    relatedTopicName:
      "哈伯星系分類法 / 巨型橢圓星系與星系併合 / 麥哲倫星雲與麥哲倫流 / 銀河系與仙女座星系未來碰撞模擬[cite: 1]",
  },
  "https://openstax.org/l/30sloansurvey": {
    id: "ID 51",
    title: "矮星系 (Dwarf Galaxy)",
    description:
      "規模遠小於標準星系的微型星系（僅數百萬至數十億顆恆星），常作為大型星系的衛星星系被重力潮汐吞噬[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 26 章[cite: 1]",
      "維基百科「矮星系」條目[cite: 1]",
    ],
    relatedTopicName: "星系吞噬與潮汐流[cite: 1]",
  },
  "https://eso.org/": {
    id: "ID 53",
    title: "三角座星系 (Triangulum / M33)",
    description:
      "本星系群中第三大的螺旋星系，距離約 300 萬光年，規模僅次於仙女座星系與銀河系[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 25 章[cite: 1]",
      "維基百科「三角座星系」條目[cite: 1]",
    ],
    relatedTopicName: "本星系群與星系自轉曲線[cite: 1]",
  },
  "https://skyandtelescope.org/astronomy-news/gotcha-firm-evidence-for-a-neutron-star-in-supernova-1987a/":
    {
      id: "ID 54",
      title: "大麥哲倫星雲 (LMC) 與 小麥哲倫星雲",
      description:
        "銀河系最近的兩個不規則伴星系（距離約 16 萬光年），南半球肉眼可見，為研究恆星演化與變星的聖地[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 19 章與第 26 章[cite: 1]",
        "維基百科「大麥哲倫星系」條目[cite: 1]",
      ],
      relatedTopicName: "超新星 1987A 爆發觀測[cite: 1]",
    },
  "http://www.atlasoftheuniverse.com/localgr.html": {
    id: "ID 55",
    title: "本星系群 (Local Group)",
    description:
      "包含銀河系、仙女座星系、三角座星系及約 60 個矮星系的重力束縛星系群，跨越約 300 萬光年[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 25 章與第 28 章[cite: 1]",
      "維基百科「本星系群」條目[cite: 1]",
    ],
    relatedTopicName: "本星系群地圖與暗物質暈[cite: 1]",
  },
  "https://en.wikipedia.org/wiki/Dark_matter": {
    id: "ID 56 / ID 115",
    title: "室女座星系團與后髮座星系團 / 暗物質與暗能量",
    description:
      "室女座星系團包含數千個星系（距 5000 萬光年）；后髮座星系團距約 3 億光年，茲威基曾在此首度推算暗物質證據[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 28 章[cite: 1]",
      "維基百科「室女座星系團」條目[cite: 1]",
    ],
    relatedTopicName:
      "茲威基與后髮座星系團暗物質發現歷史 / ΛCDM 標準宇宙學模型[cite: 1]",
  },
  "http://irfu.cea.fr/cosmography": {
    id: "ID 57",
    title: "室女座超星系團 與 拉尼亞凱亞超星系團",
    description:
      "本星系群所在的超星系團結構；拉尼亞凱亞為包含室女座超星系團在內的大型超星系團（包含十萬個星系）[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 25 章與第 28 章[cite: 1]",
      "維基百科「拉尼亞凱亞超星系團」條目[cite: 1]",
    ],
    relatedTopicName: "宇宙大尺度結構與纖維狀結構[cite: 1]",
  },
  "https://www.sdss.org/": {
    id: "ID 58 / ID 308",
    title: "宇宙網與空洞 / 史隆數位巡天 (SDSS)",
    description:
      "宇宙中的星系與星系團在超大尺度上交織成的絲狀結構（網狀），其間分布著巨大、相對貧瘠的黑暗空洞[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 28 章[cite: 1]",
      "維基百科「宇宙網」條目[cite: 1]",
    ],
    relatedTopicName:
      "史隆數位巡天 (SDSS) 三維宇宙地圖 / SDSS 官方巡天資料庫[cite: 1]",
  },
  "https://science.nasa.gov/universe/black-holes/": {
    id: "ID 59 / ID 68",
    title: "黑洞 / TON 618",
    description:
      "大量物質被壓縮至極小空間內所形成的高密度天體，其強大重力使逃逸速度超過光速[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 24 章[cite: 1]",
      "NASA Science「Black Holes」專題[cite: 1]",
      "維基百科「黑洞」條目[cite: 1]",
    ],
    relatedTopicName: "廣義相對論與時空彎曲 / 超大質量類星體[cite: 1]",
  },
  "http://blackholes.stardate.org/": {
    id: "ID 60",
    title: "事件視界 (Event Horizon)",
    description:
      "黑洞周圍單向只進不出的臨界面邊界，逃逸速度等於光速，內部訊號無法傳遞至外部宇宙[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 24 章[cite: 1]",
      "維基百科「事件視界」條目[cite: 1]",
    ],
    relatedTopicName: "卡爾·史瓦西與愛因斯坦場方程式精確解[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E5%8F%B2%E7%93%A6%E8%A5%BF%E5%8D%8A%E5%BE%91":
    {
      id: "ID 61 / ID 105",
      title: "史瓦西半徑 / 逃逸速度 (Escape Velocity)",
      description:
        "球對稱無自轉黑洞的事件視界半徑公式為 r_s = (2GM)/(c^2)。太陽的史瓦西半徑約為 3 公里，地球約為 9 毫米[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 24 章[cite: 1]",
        "維基百科「史瓦西半徑」條目[cite: 1]",
      ],
      relatedTopicName:
        "史瓦西黑洞物理計算 / 史瓦西半徑推導與光速逃逸[cite: 1]",
    },
  "https://openstax.org/l/30ndegtystidfor": {
    id: "ID 62",
    title: "奇點 (Singularity)",
    description:
      "物質在黑洞中心被重力無限壓縮至體積為零、密度無限大的幾何點[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 24 章[cite: 1]",
      "維基百科「奇點」條目[cite: 1]",
    ],
    relatedTopicName: "量子重力理論與奇點解[cite: 1]",
  },
  "https://chandra.harvard.edu/xray_sources/blackholes.html": {
    id: "ID 63 / ID 67",
    title: "吸積盤 / 天鵝座 X-1 (Cygnus X-1)",
    description:
      "氣體與塵埃落入黑洞或緻密天體時因角動量守恆形成的旋轉盤狀結構，摩擦生熱可達數百萬至數億度並發出 X 射線[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 24 章與第 27 章[cite: 1]",
      "維基百科「吸積盤」條目[cite: 1]",
    ],
    relatedTopicName: "X 射線雙星與黑洞搜尋 / 強 X 射線雙星觀測[cite: 1]",
  },
  "https://www.youtube.com/watch?v=h1iJXOUMJpg": {
    id: "ID 64",
    title: "義大利麵化 (Spaghettification)",
    description:
      "物體靠近黑洞時，因頭腳兩端承受極端潮汐力差而被縱向拉長、橫向擠壓撕裂的現象[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 24 章[cite: 1]",
      "NASA Science「Black Holes」專題[cite: 1]",
      "維基百科「義大利麵化」條目[cite: 1]",
    ],
    relatedTopicName: "潮汐破壞事件 (TDE)[cite: 1]",
  },
  "https://pweb.cfa.harvard.edu/research/topic/black-holes": {
    id: "ID 65",
    title: "超大質量黑洞 (Supermassive Black Hole)",
    description:
      "質量達太陽數十萬倍至數百億倍的巨型黑洞，普遍存在於大型星系核心[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 27 章[cite: 1]",
      "維基百科「超大質量黑洞」條目[cite: 1]",
    ],
    relatedTopicName: "活動星系核 (AGN) 與星系協同演化[cite: 1]",
  },
  "https://www.galacticcenter.astro.ucla.edu/": {
    id: "ID 66",
    title: "人馬座 A* (Sagittarius A*)",
    description:
      "位於銀河系中心的超大質量黑洞，質量約為 400 萬倍太陽質量，事件視界半徑約 1200 萬公里[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 25 章[cite: 1]",
      "NASA Science「Black Holes」專題[cite: 1]",
      "維基百科「人馬座A*」條目[cite: 1]",
    ],
    relatedTopicName: "安德烈婭·蓋茲與銀河系中心黑洞諾貝爾獎研究[cite: 1]",
  },
  "https://eventhorizontelescope.org/": {
    id: "ID 69 / ID 303",
    title: "M87 中心黑洞 / 事件視界望遠鏡 (EHT)",
    description:
      "質量約 65 億倍太陽質量的巨型黑洞。2019 年由事件視界望遠鏡 (EHT) 拍下人類史上第一張黑洞事件視界陰影影像[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 27 章[cite: 1]",
      "EHT 官方筆記[cite: 1]",
      "維基百科「M87*」條目[cite: 1]",
    ],
    relatedTopicName:
      "事件視界望遠鏡 (EHT) 國際合作計畫 / EHT 官方網站與黑洞影像公布[cite: 1]",
  },
  "https://openstax.org/l/30NASAjetprop": {
    id: "ID 70",
    title: "分子雲 (Molecular Cloud)",
    description:
      "跨越數百光年、溫度極低（約 10 K）且富含分子態氫與塵埃的巨大星際氣體雲，為恆星誕生的苗圃[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 20 章[cite: 1]",
      "NASA Science「Stars」專題[cite: 1]",
      "維基百科「分子雲」條目[cite: 1]",
    ],
    relatedTopicName: "星際分子與前生物化學[cite: 1]",
  },
  "https://openstax.org/l/30CALETvid": {
    id: "ID 72",
    title: "反射星雲 (Reflection Nebula)",
    description:
      "光線被周圍微小星際塵埃粒子散射而發光的雲氣，因藍光散射效率較高而呈藍色[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 20 章[cite: 1]",
      "維基百科「反射星雲」條目[cite: 1]",
    ],
    relatedTopicName: "昴宿星團與藍色反射星雲[cite: 1]",
  },
  "http://www.nasonline.org/publications/biographical-memoirs/memoir-pdfs/barnard-edward.pdf":
    {
      id: "ID 73",
      title: "暗星雲 (Dark Nebula)",
      description:
        "高密度的星際塵埃雲，遮擋背後遠方恆星的光線，在天空中呈現漆黑的剪影（如 Barnard 68）[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 20 章[cite: 1]",
        "維基百科「暗星雲」條目[cite: 1]",
      ],
      relatedTopicName: "巴納德暗星雲目錄[cite: 1]",
    },
  "https://www.astronomy.com/observing/the-skys-top-10-colorful-planetary-nebulae/":
    {
      id: "ID 74",
      title: "行星狀星雲 (Planetary Nebula)",
      description:
        "中低質量恆星晚期拋散出的擴張氣體殼層，被中央遺留的極熱白矮星紫外光照射發光[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 22 章[cite: 1]",
        "維基百科「行星狀星雲」條目[cite: 1]",
      ],
      relatedTopicName: "環狀星雲 M57 與蝶狀星雲[cite: 1]",
    },
  "https://openstax.org/l/30OriNebula": {
    id: "ID 75",
    title: "獵戶座大星雲 (Orion Nebula / M42)",
    description:
      "距離地球約 1300 光年、肉眼可見的著名發光 H II 星雲與恆星形成區，內部包含四合星 Trapezium 聚星[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 20 章與第 21 章[cite: 1]",
      "維基百科「獵戶座大星雲」條目[cite: 1]",
    ],
    relatedTopicName: "韋伯望遠鏡觀測獵戶座星雲原行星盤[cite: 1]",
  },
  "https://openstax.org/l/30crabnebslide": {
    id: "ID 76",
    title: "蟹狀星雲 (Crab Nebula / M1)",
    description:
      "1054 年超新星爆炸 (SN 1054) 留下的擴張殘骸，中心包含一顆每秒自轉 30 次的高能脈衝星[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 23 章[cite: 1]",
      "維基百科「蟹狀星雲」條目[cite: 1]",
    ],
    relatedTopicName: "韋伯望遠鏡與哈伯望遠鏡蟹狀星雲對照[cite: 1]",
  },
  "http://www.spacetelescope.org/videos/heic1307a/": {
    id: "ID 77",
    title: "馬頭星雲 (Horsehead Nebula)",
    description:
      "位於獵戶座、形狀極似馬頭的著名暗星雲（Barnard 33），剪影襯托在背後紅色的發光氣體前[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 20 章[cite: 1]",
      "維基百科「馬頭星雲」條目[cite: 1]",
    ],
    relatedTopicName: "近紅外線紅外巡天下的馬頭星雲[cite: 1]",
  },
  "https://openstax.org/l/30SchmidtIntv": {
    id: "ID 78",
    title: "類星體 / 活動星系核 (Quasar / AGN)",
    description:
      "早期宇宙中由中心超大質量黑洞劇烈吸積物質產生極高光度（超出一千個正常星系總和）的河外天體[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 27 章[cite: 1]",
      "維基百科「類星體」條目[cite: 1]",
    ],
    relatedTopicName: "施密特發現 3C 273 類星體高紅移[cite: 1]",
  },

  // ⏳ 物理與宇宙學 (ID 101 ~ 117)
  "https://zh.wikipedia.org/zh-tw/%E8%90%AC%E6%9C%89%E5%BC%95%E5%8A%9B%E5%B8%B8%E6%95%B8":
    {
      id: "ID 101",
      title: "牛頓萬有引力定律",
      description:
        "宇宙中任兩質點沿連心線相互吸引，引力大小與質量乘積成正比、與距離平方成反比 (F = GMm / r^2)[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 3 章[cite: 1]",
        "維基百科「萬有引力定律」條目[cite: 1]",
      ],
      relatedTopicName: "卡文迪西扭秤實驗測量引力常數 G[cite: 1]",
    },
  "https://science.nasa.gov/universe/overview/forces/": {
    id: "ID 102",
    title: "四大基本作用力",
    description:
      "重力、電磁力、強核力與弱核力，共同主宰宇宙中從粒子到星系的所有交互作用[cite: 1]。",
    sources: [
      "NASA Science「Four Forces」專題[cite: 1]",
      "維基百科「四大基本交互作用」條目[cite: 1]",
    ],
    relatedTopicName: "大統一理論 (GUT) 與力的凍結[cite: 1]",
  },
  "https://openstax.org/l/30kepsecond": {
    id: "ID 103",
    title: "克卜勒行星運動三大定律",
    description:
      "橢圓定律（太陽位於焦點）、面積定律（等時間掃過等面積）、週期定律（P^2 ∝ a^3），精確描述天體軌道[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 3 章 第 1 節[cite: 1]",
      "維基百科「克卜勒定律」條目[cite: 1]",
    ],
    relatedTopicName: "克卜勒第二定律示範模擬[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-cn/%E6%B4%BB%E5%8A%9B%E5%85%AC%E5%BC%8F": {
    id: "ID 104",
    title: "活力公式 (Vis-Viva Equation)",
    description:
      "二體問題中描述軌道上任一點瞬時速度與機械能守恆的公式 (v^2 = GM(2/r - 1/a))[cite: 1]。",
    sources: ["維基百科「活力公式」與「克卜勒軌道」條目[cite: 1]"],
    relatedTopicName: "二體問題與圓錐曲線軌道[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E8%BB%8C%E9%81%93%E6%A0%B9%E6%95%B8": {
    id: "ID 106",
    title: "軌道根數 (Orbital Elements)",
    description:
      "完整描述三維克卜勒軌道姿態與位置所需的六個獨立參數（半長軸、離心率、傾角、升交點經度、近心點幅角、真近點角）[cite: 1]。",
    sources: ["維基百科「軌道根數」條目[cite: 1]"],
    relatedTopicName: "軌道狀態向量轉換[cite: 1]",
  },
  "https://zh.wikipedia.org/zh-tw/%E8%BB%8C%E9%81%93_(%E5%A4%A9%E9%AB%94%E5%8A%9B%E5%AD%B8)":
    {
      id: "ID 107",
      title: "霍曼轉移軌道與重力助推",
      description:
        "霍曼轉移為最省燃料的切向雙脈衝橢圓軌道變軌；重力助推為利用行星重力場借力加速航向深空的技術[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 3 章[cite: 1]",
        "維基百科「霍曼轉移軌道」條目[cite: 1]",
      ],
      relatedTopicName: "航海家號行星際重力助推軌道[cite: 1]",
    },
  "https://www.ligo.caltech.edu/page/what-are-gw": {
    id: "ID 108 / ID 304",
    title: "廣義相對論與重力波 / 雷射干涉重力波天文台 (LIGO)",
    description:
      "愛因斯坦提出重力為質量彎曲時空的幾何效應；天體加速運動會產生以光速傳播的時空漣漪重力波[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 24 章[cite: 1]",
      "LIGO 官方筆記[cite: 1]",
      "維基百科「廣義相對論」條目[cite: 1]",
    ],
    relatedTopicName:
      "LIGO 雷射干涉重力波偵測器 / Caltech LIGO 實驗室與重力波科學[cite: 1]",
  },
  "https://openstax.org/l/30gravitlensing": {
    id: "ID 109",
    title: "重力透鏡 (Gravitational Lensing)",
    description:
      "大質量天體（如黑洞或星系團）強大重力彎曲背景天體發出的光線，造成影像放大、扭曲、形成愛因斯坦環或弧影[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 28 章[cite: 1]",
      "維基百科「重力透鏡」條目[cite: 1]",
    ],
    relatedTopicName: "Abell 2218 星系團重力透鏡影像[cite: 1]",
  },
  "https://openstax.org/l/30interhr": {
    id: "ID 112",
    title: "赫羅圖 (H-R Diagram)",
    description:
      "表面溫度對絕對光度（或光譜型對絕對星等）的散布圖，是研究恆星結構與演化的「元素週期表」[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 18 章 第 4 節[cite: 1]",
      "維基百科「赫羅圖」條目[cite: 1]",
    ],
    relatedTopicName: "互動式赫羅圖探索工具[cite: 1]",
  },
  "http://www.skyandtelescope.com/astronomy-equipment/the-spectral-types-of-stars/":
    {
      id: "ID 113",
      title: "視差、秒差距與星等",
      description:
        "地球公轉基線帶來的周年視差（1 角秒對應 1 秒差距/3.26 光年）；視星等代表視覺明暗，絕對星等代表距離 10 秒差距處的真實發光度[cite: 1]。",
      sources: [
        "OpenStax 天文學教科書 第 17 章與第 19 章[cite: 1]",
        "維基百科「恆星視差」與「星等」條目[cite: 1]",
      ],
      relatedTopicName: "喜帕恰斯與古星等系統歷史[cite: 1]",
    },
  "https://www.iau.org/news/pressreleases/detail/iau1812/": {
    id: "ID 114",
    title: "都卜勒效應、紅移與哈伯定律",
    description:
      "天體運動造成光譜線藍移或紅移；哈伯定律（v = H_0 × d）證明遙遠星系退行速度與距離成正比，揭示宇宙均勻膨脹[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 26 章 第 5 節[cite: 1]",
      "維基百科「哈伯定律」條目[cite: 1]",
    ],
    relatedTopicName: "哈伯常數 tension 與宇宙膨脹[cite: 1]",
  },
  "https://en.wikipedia.org/wiki/Cosmic_microwave_background": {
    id: "ID 116 / ID 306",
    title: "大霹靂、微波背景與宇宙暴脹 / COBE、WMAP 與 普朗克衛星",
    description:
      "138 億年前宇宙創生於高溫高密狀態；CMB 為 38 萬年時退耦的殘餘輝光（2.73 K）；暴脹理論解釋了宇宙的平坦性與平滑性[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 29 章[cite: 1]",
      "CMB 完整筆記[cite: 1]",
      "維基百科「大霹靂」條目[cite: 1]",
    ],
    relatedTopicName:
      "Planck 衛星全天 CMB 測繪地圖 / Planck 衛星 CMB 功率譜與宇宙學參數[cite: 1]",
  },
  "https://www.seti.org/fermi-paradox-0": {
    id: "ID 117",
    title: "德雷克方程式與費米悖論",
    description:
      "德雷克方程式估算銀河系具備通訊能力的智慧文明數量；費米悖論提出「若外星文明普遍存在，他們在哪裡？」的思考命題[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 30 章[cite: 1]",
      "維基百科「德雷克方程式」條目[cite: 1]",
    ],
    relatedTopicName: "法蘭克·德雷克與 SETI 搜尋歷史[cite: 1]",
  },

  // 🔭 觀測儀器、天文台與太空任務 (ID 301 ~ 311)
  "https://science.nasa.gov/mission/hubble/": {
    id: "ID 301",
    title: "哈伯太空望遠鏡 (HST)",
    description:
      "1990 年發射、口徑 2.4 公尺的近地軌道太空望遠鏡，涵蓋紫外、可見光與近紅外光。曾進行 Type Ia 超新星距離量測（證實宇宙加速膨脹）與拍攝深空場[cite: 1]。",
    sources: [
      "Hubble 專題筆記[cite: 1]",
      "OpenStax 天文學教科書 第 26 章[cite: 1]",
      "維基百科「哈伯太空望遠鏡」條目[cite: 1]",
    ],
    relatedTopicName: "NASA Hubble 官方任務專頁[cite: 1]",
  },
  "https://webbtelescope.org/contents/articles/whats-in-webbs-toolkit": {
    id: "ID 302",
    title: "韋伯太空望遠鏡 (JWST)",
    description:
      "2021 年發射、主鏡口徑 6.5 公尺（18 片鍍金六角形鏡片）的紅外線太空望遠鏡，運行於 L2 軌道，專為觀測早期宇宙高紅移星系與系外行星大氣設計[cite: 1]。",
    sources: [
      "JWST 專題筆記[cite: 1]",
      "OpenStax 天文學教科書 第 28 章[cite: 1]",
      "維基百科「詹姆斯·韋伯太空望遠鏡」條目[cite: 1]",
    ],
    relatedTopicName: "STScI JWST 觀測儀器與科學工具[cite: 1]",
  },
  "https://www.esa.int/Science_Exploration/Space_Science/Gaia": {
    id: "ID 305",
    title: "蓋亞衛星與依巴谷衛星",
    description:
      "依巴谷衛星首次從太空精確量測數萬恆星視差；蓋亞衛星 (Gaia) 則精確測量超過 10 億顆恆星的三維位置、視差與自行，繪製銀河系三維地圖[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章[cite: 1]",
      "維基百科「蓋亞任務」與「依巴谷衛星」條目[cite: 1]",
    ],
    relatedTopicName: "ESA Gaia 任務專頁[cite: 1]",
  },
  "https://openstax.org/l/30UFOconspiracy1": {
    id: "ID 309",
    title: "航海家 1 號/2 號與先鋒 10 號/11 號",
    description:
      "人類發射飛離太陽系的深空探測器，航海家號攜帶錄有地球影像與聲音的「黃金唱片」航向星際空間，航海家 1 號現已進入星際介質[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 19 章與第 30 章[cite: 1]",
      "維基百科「航海家計畫」條目[cite: 1]",
    ],
    relatedTopicName: "航海家黃金唱片內容與星際訊息[cite: 1]",
  },
  "https://parkersolarprobe.jhuapl.edu/index.php": {
    id: "ID 310",
    title: "帕克太陽探測器 (Parker Solar Probe)",
    description:
      "NASA 於 2018 年發射的太陽探測器，直接穿越太陽外層日冕大氣，實地測量太陽風與磁場結構，為人類史上速度最快的人造飛行器[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 15 章[cite: 1]",
      "維基百科「帕克太陽探測器」條目[cite: 1]",
    ],
    relatedTopicName: "JHUAPL 帕克太陽探測器任務專頁[cite: 1]",
  },
  "https://public.nrao.edu/gallery/nrao-video-webcast-hl-tau/": {
    id: "ID 311",
    title: "ALMA 與 甚大天線陣 (VLA)",
    description:
      "ALMA 位於智利高山毫米波陣列，擅長高解析度觀測原行星盤結構（如 HL Tau 縫隙）；VLA 位於美國新墨西哥州，用於高解析度電波天體成像[cite: 1]。",
    sources: [
      "OpenStax 天文學教科書 第 21 章與第 25 章[cite: 1]",
      "維基百科「ALMA」與「甚大天線陣」條目[cite: 1]",
    ],
    relatedTopicName: "NRAO 甚大天線陣與星際分子觀測[cite: 1]",
  },
};
