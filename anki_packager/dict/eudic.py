from anki_packager.logger import logger
import aiohttp

# https://my.eudic.net/OpenAPI/doc_api_study#-studylistapi-getcategory


class EUDIC:
    def __init__(self, token: str, id: str):
        self.id = id
        self.token = token
        self.header = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        }
        self.studylist_url = (
            "https://api.frdic.com/api/open/v1/studylist/category?language=en"
        )

        self.words_url = "https://api.frdic.com/api/open/v1/studylist/words/"

    async def get_studylist(self):
        async with aiohttp.request(
            "GET", self.studylist_url, headers=self.header
        ) as response:
            self.check_token(response.status)
            json = await response.json()
            # show list id
            for book in json["data"]:
                logger.info(f"id: {book['id']}, name: {book['name']}")

            return json

    def get_words(self):
        all_words = []
        page = 0
        page_size = 100  # 欧路API单次请求最大支持100
        
        while True:
            # 按照官方文档示例拼接 URL，确保包含 page, page_size 和 sort 参数
            url = f"{self.words_url}?language=en&category_id={self.id}&page={page}&page_size={page_size}&sort=asc"
            
            response = requests.get(url, headers=self.header)
            self.check_token(response.status_code)
            
            json_data = response.json()
            # 从返回的 JSON 中提取单词列表
            words = json_data.get("data", [])
            
            # 如果没有获取到任何单词，说明已经拉取完毕
            if not words:
                break
                
            all_words.extend(words)
            
            # 如果当前页返回的单词数小于 page_size，说明这是最后一页了
            if len(words) < page_size:
                break
                
            # 页数加1，继续获取下一页
            page += 1
            
            # 官方文档限制 page 最大为 50（即最多 5000 个单词）
            if page > 50:
                logger.warning("已达到欧路 API 的最大分页数限制（50页，最多5000词），部分单词未获取。")
                break
                
        # 保持与原代码兼容的返回结构
        return {"data": all_words, "message": ""}

    def check_token(self, status_code: int):
        if status_code != 200:
            if status_code == 401:
                msg = "前往 https://my.eudic.net/OpenAPI/Authorization 获取 token 写入配置文件"
                logger.error(msg)
                exit(1)
            else:
                msg = "检查填写的 ID 是否正确"
                logger.error(msg)
                exit(1)
