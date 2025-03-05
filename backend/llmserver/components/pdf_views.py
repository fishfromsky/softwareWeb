import os

from PyPDF2 import PdfReader, PdfWriter
import comtypes.client

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 获取PDF文件的页数（使用PdfReader）
def get_pdf_page_count(pdf_file):
    try:
        # 使用PdfReader读取PDF文件
        with open(pdf_file, 'rb') as file:
            reader = PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"读取PDF文件页数时出错：{e}")
        return 0


# 提取前30页和后30页并保存到新的PDF文件
def extract_and_save_pdf(pdf_file, output_pdf_file, max_pages=60):
    try:
        # 读取PDF文件
        with open(pdf_file, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            writer = PdfWriter()

            # 如果总页数大于max_pages，提取前30页和后30页
            if total_pages > max_pages:
                print(f"PDF文件页数：{total_pages}，超过{max_pages}页，提取前30页和后30页")
                # 提取前30页
                for i in range(30):
                    writer.add_page(reader.pages[i])
                # 提取后30页
                for i in range(total_pages - 30, total_pages):
                    writer.add_page(reader.pages[i])

            else:
                # 如果页数小于等于max_pages，直接保存所有页
                print(f"PDF文件页数：{total_pages}，未超过{max_pages}页，直接保存原始文件")
                for page in reader.pages:
                    writer.add_page(page)

            # 保存新的PDF文件
            with open(output_pdf_file, 'wb') as output_file:
                writer.write(output_file)
            print(f"新的PDF文件已保存：{output_pdf_file}")

    except Exception as e:
        print(f"提取PDF页数并保存时出错：{e}")


# 主程序
def convert_and_control_pdf_pages(word_file, pdf_file, output_pdf_file, max_pages=60):
    # 步骤1：先转换Word文件为PDF
    if not word_to_pdf(word_file, pdf_file):
        print("转换失败！")
        return

    # 步骤2：获取PDF文件页数
    current_page_count = get_pdf_page_count(pdf_file)
    print(current_page_count)

    # 步骤3：检查页数，若超过最大页数，则提取前30页和后30页
    if current_page_count > max_pages:
        print(f"警告：PDF页数超过最大页数限制！当前页数为：{current_page_count}")
        extract_and_save_pdf(pdf_file, output_pdf_file, max_pages)
    else:
        print(f"PDF文件页数符合要求，当前页数：{current_page_count}")
        # 如果页数不超过最大限制，直接保存原始PDF
        print(f"PDF文件未超过{max_pages}页，直接保存文件")
        with open(pdf_file, 'rb') as file:
            with open(output_pdf_file, 'wb') as output_file:
                output_file.write(file.read())
        print(f"PDF文件已保存：{output_pdf_file}")


# 转换Word为PDF
def word_to_pdf(word_file, pdf_file):
    try:
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False  # 不显示Word应用程序
        doc = word.Documents.Open(word_file)

        print('打开成功')

        # 保存为PDF
        doc.SaveAs(pdf_file, FileFormat=17)  # 17表示PDF格式
        doc.Close()

        # 退出Word应用
        word.Quit()

        print(f"成功转换Word文件为PDF，文件路径：{pdf_file}")
        return True
    except Exception as e:
        print(f"转换过程中发生错误：{e}")
        return False


def main_pdf(username, time):
    final_path = os.path.join(BASE_DIR, 'static', username, time)
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    # 示例：将指定的Word文件转换为PDF并控制页数不超过60页
    word_file = os.path.join(final_path, "merged_code.docx") # 替换为您的Word文件路径
    pdf_file = os.path.join(final_path, "mid_file.pdf")  # 指定保存PDF的路径
    output_pdf_file = os.path.join(final_path, "ultimate_file.pdf") # 输出PDF文件路径

    # 转换并控制PDF页数不超过60页
    convert_and_control_pdf_pages(word_file, pdf_file, output_pdf_file, max_pages=60)

