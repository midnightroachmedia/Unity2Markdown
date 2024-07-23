import sys
import os
import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QProgressBar, QLabel, QMessageBox, QRadioButton, QButtonGroup, QInputDialog
from PyQt6.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup, NavigableString
import html2text

class ConversionThread(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, files, output_dir, merge):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.merge = merge
        self.h = html2text.HTML2Text()
        self.h.body_width = 0
        self.h.unicode_snob = True
        self.h.ignore_links = True
        self.h.ignore_images = True
        self.h.ignore_anchors = True
        self.h.ignore_emphasis = False
        self.h.ignore_tables = False
        self.is_cancelled = False
        self.merged_content = []

    def run(self):
        try:
            total_files = len(self.files)
            for i, file in enumerate(self.files):
                if self.is_cancelled:
                    break
                content = self.convert_to_markdown(file)
                if self.merge:
                    self.merged_content.append(content)
                else:
                    output_path = os.path.join(self.output_dir, f"{os.path.splitext(os.path.basename(file))[0]}.md")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                self.progress.emit(i + 1, total_files)
            
            if not self.is_cancelled:
                self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def convert_to_markdown(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content = soup.find('main') or soup.find('body')
        
        if main_content:
            self.preprocess_html(main_content)
            markdown_content = self.h.handle(str(main_content))
            markdown_content = self.postprocess_markdown(markdown_content)
            return markdown_content
        return ""

    def preprocess_html(self, soup):
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()

        for element in soup.find_all(class_=re.compile('unity-')):
            if 'unity-code-block' in element.get('class', []):
                element.name = 'pre'
            elif 'unity-note' in element.get('class', []):
                element.name = 'blockquote'

        for a in soup.find_all('a'):
            a.replace_with(a.text)

        for img in soup.find_all('img'):
            img.decompose()

    def postprocess_markdown(self, content):
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'^#{1,6}\s', line):
                lines[i] = f"\n{line}\n"
        content = '\n'.join(lines)
        
        return content

    def cancel(self):
        self.is_cancelled = True

class Unity2Markdown(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.select_files_btn = QPushButton('Select HTML Files')
        self.select_files_btn.clicked.connect(self.select_files)
        layout.addWidget(self.select_files_btn)

        self.select_output_btn = QPushButton('Select Output Directory')
        self.select_output_btn.clicked.connect(self.select_output_dir)
        layout.addWidget(self.select_output_btn)

        merge_layout = QHBoxLayout()
        self.merge_group = QButtonGroup()
        self.merge_radio = QRadioButton('Merge into single file')
        self.separate_radio = QRadioButton('Create separate files')
        self.merge_group.addButton(self.merge_radio)
        self.merge_group.addButton(self.separate_radio)
        self.separate_radio.setChecked(True)
        merge_layout.addWidget(self.merge_radio)
        merge_layout.addWidget(self.separate_radio)
        layout.addLayout(merge_layout)

        button_layout = QHBoxLayout()
        self.convert_btn = QPushButton('Convert')
        self.convert_btn.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.convert_btn)

        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.file_counter_label = QLabel('0 / 0')
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.file_counter_label)
        layout.addLayout(progress_layout)

        self.status_label = QLabel('Ready to convert')
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setWindowTitle('Unity2Markdown Converter v1.1')
        self.setGeometry(300, 300, 500, 250)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select HTML Files', '', 'HTML Files (*.html)')
        if files:
            self.files = files
            self.status_label.setText(f'{len(files)} files selected')

    def select_output_dir(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if dir:
            self.output_dir = dir
            self.status_label.setText(f'Output directory: {dir}')

    def start_conversion(self):
        if not hasattr(self, 'files') or not hasattr(self, 'output_dir'):
            self.status_label.setText('Please select input files and output directory')
            return

        merge = self.merge_radio.isChecked()

        self.conversion_thread = ConversionThread(self.files, self.output_dir, merge)
        self.conversion_thread.progress.connect(self.update_progress)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.error.connect(self.conversion_error)
        self.conversion_thread.start()

        self.convert_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText('Converting...')

    def update_progress(self, current, total):
        progress_percentage = int((current / total) * 100)
        self.progress_bar.setValue(progress_percentage)
        self.file_counter_label.setText(f'{current} / {total}')

    def conversion_finished(self):
        if self.merge_radio.isChecked():
            self.get_merge_filename()
        else:
            self.show_completion_popup()
        self.reset_application()

    def get_merge_filename(self):
        filename, ok = QInputDialog.getText(self, 'Merge Filename', 'Enter the name for the merged file:')
        if ok and filename:
            if not filename.endswith('.md'):
                filename += '.md'
            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n\n---\n\n".join(self.conversion_thread.merged_content))
            self.show_completion_popup()
        else:
            QMessageBox.warning(self, 'Warning', 'Merged file was not saved. Conversion cancelled.')

    def conversion_error(self, error_message):
        self.reset_application()
        QMessageBox.critical(self, 'Error', f"An error occurred during conversion:\n\n{error_message}")

    def cancel_conversion(self):
        if hasattr(self, 'conversion_thread'):
            self.conversion_thread.cancel()
        self.reset_application()

    def show_completion_popup(self):
        QMessageBox.information(self, 'Conversion Complete', 'The HTML to Markdown conversion has been completed successfully!')

    def reset_application(self):
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.file_counter_label.setText('0 / 0')
        self.status_label.setText('Ready to convert')
        if hasattr(self, 'files'):
            del self.files
        if hasattr(self, 'output_dir'):
            del self.output_dir

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = Unity2Markdown()
    converter.show()
    sys.exit(app.exec())


