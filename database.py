import pandas as pd

class DataLoader:
    def __init__(self, path="./data"):
        self.path = path
        self.users_df, self.products_df, self.behavior_df, self.ratings_df = self._load_all_data()
        self.avg_ratings = self.ratings_df.groupby("product_id")["rating"].mean().to_dict()

    def _load_all_data(self):
        try:
            u = pd.read_excel(f"{self.path}/users.xlsx")
            p = pd.read_excel(f"{self.path}/products.xlsx")
            b = pd.read_excel(f"{self.path}/behavior.xlsx")
            r = pd.read_excel(f"{self.path}/ratings.xlsx")
            for df in [u, p, b, r]:
                df.columns = [str(c).strip() for c in df.columns]
            return u, p, b, r
        except Exception as err:
            raise RuntimeError(f"Data load error: {err}")

    def get_user(self, uid):
        res = self.users_df[self.users_df["user_id"] == uid]
        return res.iloc[0] if not res.empty else None

# إنشاء نسخة واحدة ليتم استيرادها في الملفات الأخرى
db = DataLoader()