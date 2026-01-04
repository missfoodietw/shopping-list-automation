import pandas as pd
import re
import glob

def generate_shopping_list(order_filepath, mapping_url):
    """
    根據訂單檔案和 GitHub 上的商品店家對應表，自動產生分門別類的採購清單。

    :param order_filepath: 本機的訂單檔案路徑 (Excel/CSV)。
    :param mapping_url: GitHub 上商品店家對應表的 "Raw" 連結。
    """
    try:
        # 讀取本機的訂單檔案
        orders_df = pd.read_excel(order_filepath)
        # 直接從 GitHub URL 讀取最新的店家對應表
        # engine='openpyxl' 是為了確保能正確讀取 .xlsx 格式
        mapping_df = pd.read_excel(mapping_url, engine='openpyxl')
        print("✅ 成功從 GitHub 讀取最新店家對應表。")
    except Exception as e:
        print(f"❌ 讀取檔案時發生錯誤: {e}")
        print("請檢查：")
        print("1. 本機訂單檔案路徑是否正確。")
        print("2. GitHub 對應表連結是否為 'Raw' 連結，且專案為公開。")
        return

    # --- 資料處理與匹配 (與前一版相同) ---

    def extract_brand(name):
        if not isinstance(name, str):
            return None
        match = re.search(r"【(.*?)】", name)
        if match:
            return match.group(1).strip()
        return None

    orders_df.loc[:, 'brand'] = orders_df['Product Name'].apply(extract_brand)
    mapping_df.loc[:, 'brand'] = mapping_df['商品名稱'].apply(extract_brand)

    merged_df = pd.merge(
        orders_df,
        mapping_df.drop(columns=['商品名稱']), # 避免欄位重複
        on='brand',
        how='left'
    )

    merged_df['採購店家'] = merged_df['採購店家'].fillna('店家未找到 (Not Found)')

    shopping_list_df = merged_df.groupby(
        ['採購店家', 'Product Name', 'Variation Name']
    )['Quantity'].sum().reset_index()

    # --- 輸出採購清單 (與前一版相同) ---

    print("\n========================================")
    print("      ✨ 本週自動化採購清單 ✨")
    print("========================================")

    stores = shopping_list_df['採購店家'].unique()

    for store in sorted(stores):
        print(f"\n🛒 店家: {store}\n")
        store_items = shopping_list_df[shopping_list_df['採購店家'] == store]
        output_items = store_items[['Product Name', 'Variation Name', 'Quantity']].rename(columns={
            'Product Name': '商品名稱',
            'Variation Name': '規格',
            'Quantity': '數量'
        })
        output_items['規格'] = output_items['規格'].fillna('-')
        print(output_items.to_markdown(index=False))
        print("\n" + "="*40)


if __name__ == '__main__':
    # --- 使用者設定 ---

    # ❗❗❗ 重要：請將底下的連結替換成您自己的 `商品店家對應表.xlsx` 的 "Raw" 連結！
    mapping_github_url = "https://raw.githubusercontent.com/missfoodietw/shopping-list-automation/4f1ad69dd41c42edd320f12058a10194b966f949/%E5%95%86%E5%93%81%E5%BA%97%E5%AE%B6%E5%B0%8D%E6%87%89%E8%A1%A8.xlsx”
"

    try:
        order_filename = sorted(glob.glob("Order.toship.*.xlsx"))[-1]
        
        print(f"系統找到最新的訂單檔案為: '{order_filename}'")
        print(f"將從 GitHub 讀取店家對應表...")

        # 執行主功能
        generate_shopping_list(order_filename, mapping_github_url)

    except IndexError:
        print("❌ 錯誤：在當前資料夾中找不到 'Order.toship.*.xlsx' 格式的訂單檔案。")
        print("請確認您的訂單檔案名稱是否正確，並與此程式放在同一個資料夾下。")
    except Exception as e:
        print(f"❌ 發生未預期的錯誤: {e}")

