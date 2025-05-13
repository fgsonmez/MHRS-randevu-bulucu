from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import winsound
import json
import os
from datetime import datetime
import logging
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mhrs_randevu.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MhrsRandevuFind:
    def __init__(self, data):
        self.data = dict(data)
        logging.info("MHRS Randevu Bulucu başlatılıyor...")
        self.setup_driver()
        self.check_credentials()
        self.mhrsLogin()
        self.mhrs()
        
    def setup_driver(self):
        try:
            logging.info("Chrome WebDriver ayarlanıyor...")
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--incognito")
            #chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 3)
            logging.info("Chrome WebDriver başarıyla başlatıldı")
        except Exception as e:
            logging.error(f"Chrome WebDriver başlatılırken hata: {str(e)}")
            logging.error(traceback.format_exc())
            raise
        
    def check_credentials(self):
        try:
            if not self.data.get("IdentificationNum") or not self.data.get("Password"):
                logging.error("Kimlik numarası veya şifre eksik!")
                raise ValueError("Kimlik numarası ve şifre gereklidir!")
            logging.info("Kimlik bilgileri kontrol edildi")
        except Exception as e:
            logging.error(f"Kimlik bilgileri kontrolünde hata: {str(e)}")
            raise
            
    def notify_user(self, message, is_alert=False):
        try:
            print(f"\n{'!'*50}")
            print(f"SAAT: {datetime.now().strftime('%H:%M:%S')}")
            print(f"MESAJ: {message}")
            print(f"{'!'*50}\n")
            
            if is_alert:
                winsound.Beep(1000, 1000)
            
            logging.info(f"Bildirim: {message}")
        except Exception as e:
            logging.error(f"Bildirim gösterilirken hata: {str(e)}")
            
    def mhrsLogin(self):
        try:
            logging.info("MHRS giriş sayfası açılıyor...")
            self.driver.get("https://mhrs.gov.tr/vatandas/#/")
            self.driver.implicitly_wait(30)

            logging.info("Giriş bilgileri giriliyor...")
            self.wait.until(EC.visibility_of_element_located((By.ID, 'LoginForm_username')))
            self.driver.find_element(By.ID, 'LoginForm_username').send_keys(self.data["IdentificationNum"])
            self.driver.find_element(By.ID, 'LoginForm_password').send_keys(self.data["Password"])

            logging.info("Giriş butonuna tıklanıyor...")
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ant-btn.ant-btn-teal.ant-btn-block')))
            self.driver.find_element(By.CSS_SELECTOR, 'button.ant-btn.ant-btn-teal.ant-btn-block').click()
            sleep(2)
            logging.info("Giriş başarılı")
            
        except Exception as e:
            error_msg = f"Giriş hatası: {str(e)}"
            logging.error(error_msg)
            logging.error(f"Sayfa kaynağı: {self.driver.page_source[:500]}...")
            logging.error(traceback.format_exc())
            self.notify_user(error_msg, True)
            raise

    def mhrs(self):
        try:
            logging.info("MHRS ana sayfası yükleniyor...")
            self.driver.implicitly_wait(30)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id="vatandasApp"]')))

            # Popup kontrolü
            try:
                logging.info("Popup kontrolü yapılıyor...")
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class="ant-modal-confirm-btns"] [class="ant-btn"]')))
                self.driver.find_element(By.CSS_SELECTOR, '[class="ant-modal-confirm-btns"] [class="ant-btn"]').click()
                logging.info("Popup kapatıldı")
            except:
                logging.info("Popup bulunamadı veya zaten kapalı")

            # Hastane randevusu seçimi
            logging.info("Hastane randevusu seçiliyor...")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="randevu-turu-grup-article"]')))
            randevuContents = self.driver.find_elements(By.CSS_SELECTOR, '[class="randevu-turu-grup-article"]')
            for randevuContent in randevuContents:
                if "Hastane Randevusu Al" in randevuContent.get_attribute("textContent"):
                    sleep(1)
                    randevuContent.click()
                    sleep(1)
                    logging.info("Hastane randevusu seçildi")
                    break

            # Genel arama butonu
            logging.info("Genel arama butonuna tıklanıyor...")
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class="ant-btn randevu-turu-button genel-arama-button ant-btn-lg"]')))
            self.driver.find_element(By.CSS_SELECTOR, '[class="ant-btn randevu-turu-button genel-arama-button ant-btn-lg"]').click()
            sleep(1)

            # İl seçimi
            try:
                logging.info(f"İl seçiliyor: {self.data['City']}")
                il_combobox = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ant-select-selection__placeholder') and contains(text(), 'İl Seçiniz')]")))
                il_combobox.click()
                sleep(1)

                _city = self.data["City"]
                try:
                    city_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[@id='il-6']")))
                    city_element.click()
                    logging.info(f"İl seçildi: {_city}")
                except:
                    city_elements = self.driver.find_elements(By.XPATH, f"//span[contains(@class, 'ant-select-tree-node-content-wrapper')]//span[contains(@class, 'ant-select-tree-title')]//span[contains(text(), '{_city}')]")
                    clicked = False
                    for city in city_elements:
                        if city.text.strip().upper() == _city.strip().upper():
                            city.click()
                            clicked = True
                            logging.info(f"İl seçildi: {_city}")
                            break
                    if not clicked:
                        raise Exception(f"Şehir bulunamadı: {_city}")
                sleep(1)
            except Exception as e:
                logging.error(f"İl seçiminde hata: {str(e)}")
                raise

            # İlçe seçimi
            if not self.data["District"] == "FARK ETMEZ":
                try:
                    logging.info(f"İlçe seçiliyor: {self.data['District']}")
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'-FARK ETMEZ-')]")))
                    self.driver.find_elements(By.XPATH, "//div[contains(text(),'-FARK ETMEZ-')]")[0].click()
                    selectDistrict = self.driver.find_elements(By.CSS_SELECTOR, '[role="option"]')
                    for district in selectDistrict:
                        if district.text == self.data["District"]:
                            district.click()
                            logging.info(f"İlçe seçildi: {self.data['District']}")
                            sleep(1)
                            break
                except Exception as e:
                    logging.error(f"İlçe seçiminde hata: {str(e)}")
                    raise

            # Klinik seçimi
            try:
                logging.info(f"Klinik seçiliyor: {self.data['Clinic']}")
                self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Klinik Seçiniz')]")))
                self.driver.find_element(By.XPATH, "//span[contains(text(),'Klinik Seçiniz')]").click()
                _clinic = self.data["Clinic"]
                self.driver.find_element(By.XPATH, f"//span[contains(text(),'{_clinic}')]").click()
                logging.info(f"Klinik seçildi: {_clinic}")
                sleep(1)
            except Exception as e:
                logging.error(f"Klinik seçiminde hata: {str(e)}")
                raise

            # Hastane seçimi
            if not self.data["Hospital"] == "FARK ETMEZ":
                try:
                    logging.info(f"Hastane seçiliyor: {self.data['Hospital']}")
                    hospitalSelectMenu = self.driver.find_elements(By.XPATH, "//span[contains(text(),'-FARK ETMEZ-')]")[0]
                    self.wait.until(EC.element_to_be_clickable(hospitalSelectMenu))
                    hospitalSelectMenu.click()
                    _hospital = self.data["Hospital"]
                    self.driver.find_element(By.XPATH, f"//span[contains(text(),'{_hospital}')]").click()
                    logging.info(f"Hastane seçildi: {_hospital}")
                    sleep(1)
                except Exception as e:
                    logging.error(f"Hastane seçiminde hata: {str(e)}")
                    raise

            # Doktor adı filtreleme
            if self.data.get("DoctorName") and self.data["DoctorName"].strip():
                try:
                    logging.info(f"Doktor adı filtreleniyor: {self.data['DoctorName']}")
                    # Combobox'ı bul ve tıkla
                    doctor_combobox = self.wait.until(EC.element_to_be_clickable((By.ID, 'hekim-tree-select')))
                    doctor_combobox.click()
                    sleep(1)
                    
                    # Doktor listesinden seçim yap
                    doctor_name = self.data["DoctorName"]
                    doctor_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(@id, 'hekim-') and contains(text(), '{doctor_name}')]")))
                    doctor_element.click()
                    logging.info(f"Doktor seçildi: {doctor_name}")
                    sleep(1)
                except Exception as e:
                    logging.error(f"Doktor seçiminde hata: {str(e)}")
                    raise

            # Tarih seçimi
            if not self.data["StartDate"] == "FARK ETMEZ" and not self.data["EndDate"] == "FARK ETMEZ":
                try:
                    logging.info(f"Tarih aralığı seçiliyor: {self.data['StartDate']} - {self.data['EndDate']}")
                    self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class="ant-calendar-picker-input ant-input"]')))
                    date_inputs = self.driver.find_elements(By.CSS_SELECTOR, '[class="ant-calendar-picker-input ant-input"]')
                    
                    date_inputs[0].click()
                    sleep(1)
                    self.driver.find_element(By.CSS_SELECTOR, '[class="ant-calendar-input "]').send_keys(self.data["StartDate"])
                    logging.info(f"Başlangıç tarihi girildi: {self.data['StartDate']}")
                    sleep(1)
                    
                    date_inputs[1].click()
                    sleep(1)
                    self.driver.find_element(By.CSS_SELECTOR, '[class="ant-calendar-input "]').send_keys(self.data["EndDate"])
                    logging.info(f"Bitiş tarihi girildi: {self.data['EndDate']}")
                    sleep(1)
                except Exception as e:
                    logging.error(f"Tarih seçiminde hata: {str(e)}")
                    raise

            # Arama butonu
            logging.info("Arama başlatılıyor...")
            self.driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
            sleep(1)

            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="ant-page-header-heading-title"]')))

            # Randevu kontrolü
            try:
                dataMsg = self.driver.find_element(By.CSS_SELECTOR, '[class="ant-modal-confirm-content"]').text
                if "bulunamamıştır." in dataMsg:
                    logging.info("Randevu bulunamadı")
                    self.notify_user("Randevu bulunamadı.")
            except:
                try:
                    randevu_tarihleri = self.driver.find_elements(By.CSS_SELECTOR, '[class="ant-calendar-date"]')
                    tarihler = []
                    for tarih in randevu_tarihleri:
                        if tarih.get_attribute("class").find("ant-calendar-selected-date") != -1:
                            tarihler.append(tarih.text)
                    if tarihler:
                        msg = f"RANDEVU BULUNDU! Tarihler: {', '.join(tarihler)}"
                        logging.info(msg)
                        self.notify_user(msg, True)
                        # E-posta gönder
                        self.send_email(
                            "MHRS Randevu Bulundu!",
                            f"Randevu tarihleri: {', '.join(tarihler)}\n\n"
                            f"Hastane: {self.data['Hospital']}\n"
                            f"Klinik: {self.data['Clinic']}\n"
                            f"İl: {self.data['City']}\n"
                            f"İlçe: {self.data['District']}"
                        )
                    else:
                        msg = "RANDEVU BULUNDU! Hemen kontrol edin!"
                        logging.info("Randevu bulundu fakat tarihler alınamadı")
                        self.notify_user(msg, True)
                        # E-posta gönder
                        self.send_email(
                            "MHRS Randevu Bulundu!",
                            "Randevu bulundu fakat tarihler alınamadı.\n"
                            f"Hastane: {self.data['Hospital']}\n"
                            f"Klinik: {self.data['Clinic']}\n"
                            f"İl: {self.data['City']}\n"
                            f"İlçe: {self.data['District']}"
                        )
                except:
                    msg = "RANDEVU BULUNDU! Hemen kontrol edin!"
                    logging.info("Randevu bulundu")
                    self.notify_user(msg, True)
                    # E-posta gönder
                    self.send_email(
                        "MHRS Randevu Bulundu!",
                        "Randevu bulundu!\n"
                        f"Hastane: {self.data['Hospital']}\n"
                        f"Klinik: {self.data['Clinic']}\n"
                        f"İl: {self.data['City']}\n"
                        f"İlçe: {self.data['District']}"
                    )

        except Exception as e:
            error_msg = f"İşlem hatası: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.notify_user(error_msg, True)
            raise
        finally:
            logging.info("Tarayıcı kapatılıyor...")
            self.driver.quit()

    def send_email(self, subject, message):
        try:
            if not self.data.get("Email") or not self.data.get("EmailPassword"):
                logging.warning("E-posta bilgileri eksik olduğu için e-posta gönderilemedi")
                return

            # E-posta ayarları
            sender_email = self.data["Email"]
            sender_password = self.data["EmailPassword"]
            receiver_email = self.data["Email"]  # Kendine gönder

            logging.info(f"E-posta gönderimi başlatılıyor... Alıcı: {receiver_email}")

            # E-posta oluştur
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            # Mesaj gövdesi
            body = f"""
            MHRS Randevu Bildirimi
            
            {message}
            
            Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
            """
            msg.attach(MIMEText(body, 'plain'))

            # Gmail SMTP sunucusuna bağlan
            logging.info("Gmail SMTP sunucusuna bağlanılıyor...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            logging.info("Gmail hesabına giriş yapılıyor...")
            server.login(sender_email, sender_password)
            
            # E-postayı gönder
            logging.info("E-posta gönderiliyor...")
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
            
            logging.info(f"E-posta başarıyla gönderildi: {subject}")
            self.notify_user(f"E-posta bildirimi gönderildi: {receiver_email}", False)
        except Exception as e:
            error_msg = f"E-posta gönderilirken hata oluştu: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.notify_user(error_msg, True)

def load_config():
    config_file = "config.json"
    try:
        if os.path.exists(config_file):
            logging.info(f"Config dosyası bulundu: {config_file}")
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                logging.info("Config içeriği yüklendi")
                return config
        else:
            logging.error(f"Config dosyası bulunamadı: {config_file}")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"JSON dosyası okunamadı: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Config dosyası okunurken beklenmeyen hata: {str(e)}")
        return None

def main():
    logging.info("Program başlatılıyor...")
    config = load_config()
    if not config:
        logging.error("Config yüklenemediği için program sonlandırılıyor!")
        return

    while True:
        try:
            logging.info("Randevu kontrolü başlatılıyor...")
            MhrsRandevuFind(config)
            logging.info("10 dakika bekleniyor...")
            sleep(600)  # 10 dakika bekle
        except Exception as e:
            logging.error(f"Hata oluştu: {str(e)}")
            logging.error(traceback.format_exc())
            logging.info("5 dakika sonra tekrar denenecek...")
            sleep(300)  # 5 dakika bekle

if __name__ == "__main__":
    main()
