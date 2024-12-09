from flask import Flask, request, abort, jsonify
import skype_chatbot
import json
import os
import re
import time
import google.generativeai as genai
import requests

app = Flask(__name__)

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')
genai.configure(api_key="AIzaSyD8OG39WRzCydCU2l6qOmqLJkldMbFmI9o")

#read file
file_list = []
for file in genai.list_files():
    file_name=genai.get_file(file.name)
    file_list.append(file_name)

# Create the model
generation_config = {
  "temperature": 0.1,
  "top_p": 0.95,
  "top_k": 32,
  "max_output_tokens": 800,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-exp-0827",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
    {
      "role": "model",
      "parts": [
        "--- START OF FILE FAQ Testing ---\n\nquestion,answer\n什麼是atZone?,\"atZone是Horizon Fitness 為了提供會員更好的運動體驗所打造的健身 App 。\n你可免費使用例行鍛鍊程序，包含Sprint 8、配速訓練、重量訓練助手等功能。\n我們也會每月提供免費的會員專屬運動旅程點數(Z Points)，讓你隨心所欲使用虛擬實境及隨選播放等串流功能。\n若每月的免費點數用盡，我們也提供不同購買方案讓你能額外付費購買點數，已持續享受App內的串流服務。\n\n(部分國家不支援Z Points額外購買方案)\"\n如何更改atZone的顯示語言？,\"若你的行動裝置為 iOS 版本，請參考以下步驟：\n1. 至App內的「個人資訊」（Profile）點擊「個人帳號與頭像」。\n2. 點擊右上角的「編輯」。\n3. 點擊「更換語言」，App自動跳轉至 iOS 系統設定。\n4. 點擊「語言」，選取你欲修改的語言後，返回 atZone 即可修改完成。\n\n若你的行動裝置為 Android 版本，請參考以下步驟：\n1.至「個人資訊」（Profile）點擊「個人帳號與頭像」。\n2.點擊右上角的「編輯」。\n3.點擊語言欄位即會展開選單，可選擇你欲修改的語言。\"\natZone目前支援哪些健身設備？,\"atZone目前支援Horizon品牌的跑步機、健身車、橢圓機與家庭健身房設備，支援型號如下：\n[跑步機]\nTread-XP, 7.4AT-03, 7.0AT-24, Elite T7.1, Omega Z, Paragon X, T202-26, T202-SE, T101-27, Evolve 3.0, TR5.0, TR3.0, 7.0AT-25, 5.0AT-21, T9-21\n\n[健身車]\nCycle-XP, GR7, 7.0IC-22, 5.0IC-21, 3.0SC, 5.0U-21, 5.0R-21, Paros 3.0,bikeful\n\n[橢圓機]\nAndes 7.1, Andes 5.1, EX59-24, Syros 3.0\n\n[家庭健身房]\nHBN70, HCU30, HDB70, HKB70, HBN50, HBN30, HPR70, HHR50, HSR30\n\n(支援型號將持續更新，實際支援情況可於購買時同步與通路確認)\"\n將我的健身設備進行連線/登錄後，如何透過atZone開始進行我的運動？,\"將你購買的健身設備加入「健身設備」清單後，你可以於「首頁」左上角進行設備頁面的選擇與切換，選擇與你設備匹配的類型後，便可以使用該設備類型內的虛擬實境、隨選影片或例行鍛鍊程序等功能。\n\n(當你的健身設備為跑步機、健身車、橢圓機等需要透過藍牙進行連線的設備時，請確保你的設備已與App進行連線)\"\n能夠離線使用atZone的功能嗎？,atZone會於用戶登入、設定、乃至運動等過程中皆會進行資料傳輸作業，為確保體驗，請全程保持網際網路連線。\natZone可以支援什麼樣的行動裝置與作業系統？,\"atZone 目前支援 iOS 14.0 以上(含)及 Android 5.1 以上(含)。\n請確認你的行動裝置系統版本符合上述版本。\"\n如何更新atZone App？,\"App會不定期進行功能更新，可留意你的AppStore或Google Play，若有新推出版本，便會出現「更新」選項，點選後即可更新。\n同時，可於行動裝置系統設定處，將App的通知功能開啟，以確保atZone不定期更新時能夠收到推播通知。\"\n我要如何註冊新帳號？,\"請你開啟 atZone 至註冊頁，點擊註冊，並跟隨以下步驟：\n\n[以社群帳號進行註冊]\n1. 選擇欲使用的第三方社群平台(Apple, Google, Facebook)。\n2. 確認第三方社群帳號已通過驗證並登入。\n3. 填寫個人資訊並同意隱私權政策及使用條款後，點選「創立新帳號」後將完成新帳號註冊。\n\n[以Email進行註冊]\n1. 輸入你的Email與設定帳號密碼，並同意隱私權政策及使用條款後，點選「繼續」。\n2. 我們會將驗證碼寄送至你的信箱，請在 30 分鐘內輸入驗證碼以啟動你的帳號。\n3. 填寫個人資訊後點選「創立新帳號」以完成新帳號註冊。\"\n為什麼我註冊帳號後，沒有收到驗證信？,\"若你未收到 atZone 發送的驗證信，可能有下列情況：\n\n1.可能是你填寫的 Email 帳號無效或輸入錯誤，你可使用正確的 Email 再次註冊。\n2.可能是你的 Email 服務商判斷驗證信為垃圾信，建議你至垃圾郵件匣中查找，並將它設定為非垃圾郵件。\n3.可能是你的 Email 服務商之安全機制阻擋驗證信，建議你可聯絡你的 Email 服務商或是使用其他的 Email 帳號重新註冊。\n4.若你使用公司 Email 註冊，請確認貴公司之資訊安全政策不會阻擋信件。\n\"\n為什麼我的驗證碼失敗了？,\"1.請再次確認你的驗證碼是否輸入正確\n2.驗證碼超過30分鐘便會失效，請重新申請寄送驗證碼\"\n我忘記密碼了該怎麼辦？,\"若你忘記帳號密碼，可跟隨以下步驟：\n\n1. 在登入頁面中點選「忘記密碼」，\n2. 輸入註冊的電子信箱並按下「繼續」，我們會將重設密碼的認證碼寄送至你的電子信箱。\n3. 請在 30 分鐘內，依照指示輸入認證碼，即可重新設定。\"\n如何變更我的密碼與個人資料？,如果你需要變更密碼、個人資料，請至「個人資訊」內點選「編輯」，依照指示輸入即可進行重新設定。\n我可以在不同行動裝置中登入我的帳號嗎？,可以，不論是 iOS 或 Android 系統，你皆可以在不同裝置中使用同一組帳號。\n我可以刪除我的帳號嗎？,\"你可以刪除在atZone註冊的帳號，請注意刪除帳戶後所有資料將會被清除，且無法還原帳戶。\n你可以透過以下步驟刪除帳號：\n\n1. 至「個人資訊」（ Profile ）點擊「個人帳號與頭像」。\n2. 點擊右上角的「編輯」。\n3. 在選單最下方點擊「刪除帳號」。\"\n我需要付費才能使用App內功能嗎？,\"只要你擁有Horizon的健身設備，便可以透過設備連線或設備登錄來使用atZone所有功能，無需付費購買此App或App內之功能服務，亦不需支付服務訂閱等費用。\n惟當每月由atZone主動提供的免費會員專屬運動旅程點數(Z Points)用盡後，你可以選擇是否加購點數以繼續使用「虛擬實境」及「隨選播放」之內容；於此同時，無論你的點數用盡與否，「例行鍛鍊程序」皆不受點數影響，隨時都能使用。\n\n(部分國家不支援Z Points額外購買方案)\"\n我如何透過atZone與我的健身設備進行連線/登錄,\"[Cardio系列產品]\n我們將透過藍牙功能連接你的atZone App與Cardio系列設備，請透過下列步驟進行新增與連線：\n\n1. 請將你的horizon健身設備插上電源並開機。\n2. 請確認你的行動裝置已開啟藍牙功能，並打開atZone App。\n3. 至atZone的「健身設備」頁面，並點選「Cardio 系列」卡片。\n4. 點選「連接」並選擇你要連線的健身設備名稱，即可連線完成。\n5. 若你的設備清單已成功新增一台以上的健身設備，並想繼續新增其他設備時，可在「健身設備」頁面的右上方點選「＋」，並重複執行上述步驟，即可將不同設備新增至設備清單內。\n\n\n[Strength 系列產品]\n我們將透過掃描健身設備專屬QR Code以將你的Strength系列設備登錄至atZone App內，請透過下列步驟進行設備登陸：\n\n1. 請找到你的Horizon健身設備上的QR Code貼紙。\n2. 至atZone的「健身設備」頁面，並點選「Strength 系列」卡片。\n3. 點選「掃描」並將你的行動設備相機對準QR Code以進行掃描登錄作業。\n4. 成功掃描後你的健身設備將會列於健身設備清單內。\n5. 若你的設備清單已成功登錄一台以上的健身設備，並想繼續新增其他設備時，可在「健身設備」頁面的右上方點選「＋」，並重複執行上述步驟，即可將不同設備新增至設備清單內。\"\n當我打開atZone的時候，App會自動幫我將健身設備進行藍牙連線嗎？,\"用戶開啟atZone App時，App將自動針對前次加入的Cardio系列產品進行自動藍牙連線，請確認下列：\n\n1. 請確認你的健身設備已開啟並支援atZone App。\n2. 請確認你行動裝置的藍牙功能已開啟。\n3. 請確認你上次連線健身設備時，沒有在App內手動斷開藍牙連線。\n4. 當atZone App開啟時，將持續30秒以偵測周圍是否存在前次連線的健身設備，若有，將自動完成藍牙連線；超過30秒後，你必須自行手動完成藍牙連線。\"\n若我的健身設備持續無法與atZone進行藍牙連線，我該怎麼處理？,\"若你的Cardio系列設備無法與 atZone 進行藍牙連線，請確認以下情況：\n\n1. 你的 Horizon 健身設備支援 atZone App。\n2. 健身設備有插上電源並開啟。\n3. 你的行動裝置已開啟藍牙功能。\n4. 若你已將設備新增至設備清單內，仍無法成功連線，你可以嘗試 Forget Equipment 再重新新增設備。\n5. 若你的行動裝置為 Android 版本，請於「設定」>「應用程式」中，搜尋「atZone」，於隱私設定的「許可」處檢查是否允許存取你的位置，並檢查行動裝置是否有開啟位置功能。\n\n若以上步驟無法排除，請聯繫客服。\"\n若我的健身設備持續無法完成QR Code掃描，我該怎麼處理？,\"若你的 Strength系列設備無法透過 atZone 進行掃描登錄作業，請確認以下情況：\n\n1. 請確認你的Horizon 健身設備支援 atZone App並在設備機身上附有QR Code貼紙。\n2. 請確認你是否允許行動裝置的相機使用權限。\n\n若以上步驟無法排除，請聯繫客服。\"\n我該如何從我的健身設備清單內移除已加入設備？,\"你可以透過以下步驟，移除你的 Horizon 健身設備： \n1. 在「健身設備」中，點擊你的健身設備圖片旁的「....」至「More」視窗。\n2. 接著請你點擊「忘記健身設備」。\n3. 點擊「忘記」即可移除。\"\n什麼是虛擬實境功能？,\"虛擬實境是atZone特別製作的健身互動課程，在運動過程中你的設備將會隨著影片的進程自動調整速度、坡度或阻力，讓你在揮汗的同時享受全球各地風景，帶來身歷其境的獨特運動體驗。\n目前atZone規劃了全球 22 條經典路線，供你進行訓練，未來也會持續更新，提供你更多選擇。\"\n我該如何選擇虛擬實境的等級？不同等級會影響什麼？,虛擬實境中共分為20個等級，我們建議你可先評估身體狀況及欲達到的健身目標來選擇適合的運動強度。\n我可以如何與自己競賽？,在使用虛擬實境功能進行運動時，atZone會依你跑步或騎乘的努力及劇烈程度幫你計算單次運動的成績(Score)，並在你下一次使用同一影片時，將你過往最佳的成績與當前的成績進行較量，讓你知道你目前的運動狀態與你的最佳成績差距多少，並激勵你不斷挑戰自己。\n我可以如何與全球用戶競賽？,在使用虛擬實境功能進行運動時，atZone會依你跑步或騎乘的努力及劇烈程度幫你計算單次運動的成績(Score)，並將你的最佳成績列入排行榜內與全球用戶進行排名競賽，激勵你不斷向世界強者發起挑戰，爭取自己的最佳名次。\n為什麼我的虛擬實境影片出現緩衝處理、停頓或無法正常播放？,\"影片出現緩衝處理、停頓或無法正常播放的情況，可以試著透過下列方法修正問題。\n\n1. 每部影片皆需消耗對應的 Z Points ，請你確認帳戶中的 Z Points 餘額是否足夠播放該影片，若餘額不足你可透過應用程式內購買 Z Points 。\n2. 檢查網路速度，若網際網路連線速度較慢，影片可能無法正常播放。\n3. 請確認你是否已開啟手機藍牙設定並已與你的運動設備正確連接。\n4. 重新啟動裝置。\n5. 至 App Store 或 Google Play 進行應用程式更新。\"\"\"\n什麼是隨選播放功能？,\"atZone邀請全球熱門教練，提供超過上百堂的線上教學課程，讓你在家即可隨選播放影音課程，讓你可以跟著教練的陪伴與指令，豐富你的訓練體驗、加乘整體運動效果。\n\n(隨選影片會不定期持續更新)\"\n隨選播放課程是否支援多國語言或多國字幕？,\"部分隨選播放影片具備英文與中文字幕，用戶可以依需求進行切換。\natZone也會持續擴增多國語言的支援性，敬請期待。\"\n什麼是動作偵測功能？,\"開啟動作偵測時，App將使用行動裝置前置鏡頭偵測用戶動作，與教練動作進行比對，並記錄執行正確動作的次數。\n以下為必要流程及注意事項：\n\n[骨骼定位]\n為提升動作偵測準確度，將於設定過程中請用戶進行骨骼定位。\n\n[鏡像偵測]\n進行動作偵測時，請鏡像教練的動作，及教練做左，你應該做右，以確保正確偵測。\n\n[全身入鏡]\n正面全身朝向鏡頭，並確保動作進行時也能夠全身入鏡。\"\n為什麼我的隨選播放影片出現緩衝處理、停頓或無法正常播放？,\"影片出現緩衝處理、停頓或無法正常播放的情況，可以試著透過下列方法修正問題。\n\n1. 每部影片皆需消耗對應的 Z Points ，請你確認帳戶中的 Z Points 餘額是否足夠播放該影片，若餘額不足你可透過應用程式內購買 Z Points 。\n2. 檢查網路速度，若網際網路連線速度較慢，影片可能無法正常播放。\n3. 請確認你是否已開啟手機藍牙設定並已與你的運動設備正確連接。\n4. 重新啟動裝置。\n5. 至 App Store 或 Google Play 進行應用程式更新。\"\"\"\n什麼是Sprint8？我該如何進行設定？,\"Sprint 8 是喬山獨家研發的訓練系統，經過科學實證，藉由 20 分鐘的高強度間歇訓練課程，能提升能量、減少體脂肪並增長肌肉。\n用戶可以依據自己的程度進行橫跨20階的強度選擇，選擇強度並開始運動後，你的健身設備會自動在運動過程中調整速度、坡度或阻力，以輔助你完成Sprint 8課程。\"\nSprint 8內的Sweat Score是什麼？,Sweat Score 是依據你訓練時的坡度或阻力、心率及燃燒的卡路里等綜合計算出的運動成績，Sweat Score越高代表該此的運動成績越好。\n什麼是配速訓練？我該如何進行設定？,\"配速是長跑訓練中常被使用的概念，通常指每公里跑步所用的時間。\n利用配速訓練，你可以更精確地調整運動節奏、體能訓練，更有效率地突破自我極限。\n你可以依據自身體能狀況及訓練需求，設定不同段落的時速與時間，最多可設定 10 個分段。\"\n什麼是目標心率訓練？我該如何進行設定？,\"目標心率是一個用來測量運動強度的指標，你可以設定運動時間、目標心率，atZone 透過調整 Horizon 健身設備的坡度、阻力、速率，來幫助你達到目標。\n\n此訓練需要另外連接藍牙心率裝置(心率胸帶)才能正確執行。\n\n關於目標心率如何計算，可以用你的最大心率乘以運動強度%得出。\n運動強度定義可以參考美國心臟協會（ American Heart Association ）建議：\n中強度運動：最大心率的 50 ～ 70 ％\n高強度運動：最大心率的 70 ～ 85 ％\"\n什麼是重量訓練助手？我該如何進行設定與訓練？,\"重量訓練助手提供Horizon Home Gym用戶具計畫性的多樣訓練菜單，由專業教練精心設計，讓你可以依自己所期望的訓練目標與訓練部位進行不同的菜單選擇，並且你可依自己的程度與偏好進行設備重量與動作次數的設定。\n運動過程中會由專業教練先行說明與示範動作要領，並且陪伴你執行每一次的動作，帶領你達到「身型雕塑」或「增加肌肉量」等訓練成效；有規律且有計畫性地使用此功能，將可更有效地幫助你達成你所設定的訓練目標。\"\n我該如何檢視或分享我的運動紀錄？,\"在每次運動結束後，atZone會為你整理當次運動摘要，你可以透過分享按鍵，與你的親朋好友分享你的運動成果。\n同時，你也可以在「個人資訊」＞「運動紀錄」中，查看你的運動成就，並可依每週、每月、每年等時間區間進行篩選，以檢視你在各別區間內累計的運動成果。\"\n我該如何將atZone連接到第三方應用程式？連接後可以幫助我什麼？,\"atZone現在支援Apple Health、Google Fit、Fitbit和Strava等第三方應用程式。你可以連接你最喜愛的應用程式，並無縫將你在atZone的運動數據整合至你喜愛的第三方應用程式。\n設定步驟如下：\n\n1..至「個人資訊」。\n2.點擊「連接APP」。\n3.選擇您想連接的第三方軟體，按下「連接」。\n4. 根據第三方軟體指示完成連接。\"\n我該如何連接心率裝置(心率帶)？,\"正確穿戴好你的心率胸帶，開啟行動裝置的藍牙功能後，你可以透過以下 2 種方法連接atZone：\n\n方法1：\n1. 點選「首頁」右上方的「心率」符號。\n2. 在「心率裝置」頁面點選右上角的「＋」。\n3. 選取你的心率裝置，並點擊「新增」以新增並連接裝置。\n\n方法2：\n1.在「個人資訊」頁面點選「配件」。\n2. 選擇「心率裝置」。\n3. 在「心率裝置」頁面點選右上角的「＋」。\n4. 選取你的心率裝置，並點擊「新增」以新增並連接裝置。\"\n為什麼我的心率帶無法連接atZone？,\"若你的心率胸帶無法與 atZone 連接，可能有下列情況：\n\n1.請確認你的心率胸帶穿戴正確。\n2.請確認你的心率胸帶電源充足並為開啟狀態。\n3.請檢查你的行動裝置是否開啟藍牙功能。\"\natZone是否取得心率值將影響哪些運動紀錄？,\"atZone 可透過藍牙心率裝置、智慧手錶或Horizon 健身設備的心率手把獲取你的心率資訊，當atZone獲取你的心率數據時，除了會將此心率數值顯示於運動中的資訊儀表上之外，也會同時將此數據紀錄於你的運動紀錄內。\n除此之外，atZone內許多功能會透過你的心率進行消耗卡路里的計算。\n因此，建議你在運動過程中能夠透過上述任一方式讓atZone能夠獲取你的心率資訊，以獲取更完整的運動體驗。\"\n為什麼連接的Horizon健身設備顯示的數據，與atZone上呈現的數據不同？,因為藍牙傳輸時間限制偶爾會造成此情況，但不影響你最終運動數據。\n我該如何讓atZone的畫面鏡像輸出到外部顯示器？,\"[iOS裝置]\n1. 在「首頁」右上方點選「螢幕鏡像輸出」符號，將出現相關操作說明。\n2. 將你的行動裝置與欲進行「螢幕鏡像輸出」的外部顯示器連接上同一個網路環境。\n3. 打開行動裝置的控制中心，點選「螢幕鏡像輸出」。\n4. 選擇欲進行「螢幕鏡像輸出」的裝置。\n5. 返回atZone App。\n\n[Android裝置]\n1. 將你的行動裝置與欲進行「投放屏幕」的外部顯示器連接上同一個網路環境。\n2. 在「首頁」右上方點選「投放屏幕」符號。\n3. 選擇欲進行「投放屏幕」的裝置。\"\n我該如何啟用與設定app通知功能？,\"可依下列步驟啟用app推播通知功能：\n\n1. 至atZone的「個人資訊」頁面\n2. 點選「通知」，並進入通知設定頁面\n3. 打開「推播通知」，App會跳轉頁面至行動裝置系統設定頁面\n4. 於系統設定頁面內確認啟用/允許通知功能\n5. 回到atZone，即會看見「推播通知」已啟用。\"\n什麼是Z Points？什麼時候會消耗Z Points？,\"Z Points為atZone的會員點數，你可以使用Z Points以觀看「虛擬實境」及「隨選播放」等串流影音內容。\natZone 會於每個月的第一天免費贈送特定數量的Z Points，並於你使用「虛擬實境」及「隨選播放」等串流內容時依據你觀看的時長進行點數的扣除，若你的點數不足，則無法再使用串流內容；此時，你可以選擇是否購買更多Z Points已持續使用串流內容，或等待下個月提供的免費點數再作使用。\n\n(部分國家不支援Z Points額外購買方案)\"\n如何獲得Z Points？,\"你可透過下列兩種方式於 atZone 取得 Z Points：\n\n1. 每月 1 號 00：00 (UTC+0)atZone 會提供每位會員特定數量的免費 Z Points。\n2. 你可以透過本應用程式支援的付款方式購買 Z Points 點數。目前你可選擇使用 Apple 「 App 內購買」或 Google Play 「應用程式內購」 來購買 Z Points 。\n\n(在部分國家可能不可購買)\"\n我的Z Points有使用期限嗎？,\"會員專屬限時的 Z Points 使用期限為每月最後一日 23：59 ，未使用完畢的 Z Points 將歸零，無法遞延至次月使用。\n你購買的 Z Points 則沒有使用期限。\"\n我如何查詢帳戶中有多少Z Points？,你可以在「個人資訊」 >「 Z Points 頁面」看到目前擁用的 Z Points（免費／購買），亦可在紀錄選項中查詢目前 Z Points 的逐筆使用歷程。\n我如果中途離開影片，Z Points會如何計算？,\"若你中途終止影片播放，系統將會從你離開的時間點計算影片已播放時間並扣除對應的 Z Points。\n\n例如：你觀看 23 分 5 秒的虛擬實境影片，中途在 11 分 39 秒離開影片，我們將從你帳戶中扣抵 12 Z Points。\"\n我使用Z Points 時的扣抵順序是？,帳戶中的Z Points 依取得方式分為免費及付費購買兩種，我們會優先扣抵免費提供的 Z Points，若免費的Z Points 額度用盡後，才會扣抵付費購買的 Z Points。\n我購買Z Points 後，可以退款嗎?,\"如果你透過 Apple 「App 內購買」或 Google Play 「應用程式內購」購買Z Points，你可依循該系統服務商的退款流程進行申請，退款審核由服務商判定，本公司不涉及相關事項處理。\n\nApple 「App 內購買」點數：若你想申請退款，請與 Apple 官方支援小組聯繫。\n注意：申請退款僅能在購買點數的 90 天內，超過 90 天後 Apple 將不予受理。\n※ 更多說明請參考：https://support.apple.com/en-us/HT204084\n\nGoogle Play 「應用程式內購」點數：若距離你購買點數的時間尚未超過 48 小時，可透過 Google Play 申請退款。\n※ 更多說明請參考：https://support.google.com/googleplay/answer/7205930\"\n我如果更換行動裝置，會影響我擁有的Z Points嗎？,不會， Z Points 會歸屬在你註冊的會員帳號，不會因為行動裝置改變而消失。\nWhat data does the app collect?,\"atZone會收集多種類型的數據，包括您的電子郵件地址、用戶名，以及其他可選信息，如您的真實姓名、頭像、性別、年齡、身高、體重和位置。\n此外，還會收集您的運動數據，如運動時間、時長、距離、速度、坡度、燃燒的卡路里以及心率（如果使用兼容的第三方設備）。\n同時，還會收集服務使用數據、設備連接和配置數據，以及根據您的IP地址獲取的位置數據。\"\nHow is my personal data protected?,\"你的個人資訊將儲存在由公司控制的雲端伺服器上，並採取合理的安全措施，以防止未經授權的訪問、使用、修改、披露或銷毀。\n然而，仍須提醒您，任何通過互聯網進行的傳輸或存儲方式都無法完全保證安全，因此無法承諾絕對的安全性。\"\nCan I delete my account and data permanently?,是的，您可以通過帳戶設置或發送電子郵件給公司來永久刪除您的帳戶。刪除請求處理後，公司將從其伺服器上刪除您的數據。然而，一些信息可能會保留在存檔或備份副本中，並且與第三方合作夥伴共享的數據可能不會被公司刪除。公司會向第三方合作夥伴請求刪除這些數據，但這些數據可能仍然會保留在這些平台上。\natZone 官方網站介紹,這是atZone 官方網站說明 : https://global.horizonfitness.com/tw/zht/exercise-innovations/atzone\n\n--- END OF FILE FAQ Testing ---",
      ],
    },
    {
      "role": "user",
      "parts": [
        file_list[0],
        file_list[1],
        file_list[2],
      ],
    },
    {
      "role": "user",
      "parts": [
        "回答麻煩使用繁體中文。",
      ],
    },
  ]
)


# domain root
@app.route('/')
def home():
    return 'Hello, World!'

# 用來接收訊息的 Webhook
@app.route('/webhook', methods=['GET', 'POST'])
def handle_message():
    bot = skype_chatbot.SkypeBot(app_id, app_secret)
    payload = "grant_type=client_credentials&client_id=" + app_id + "&client_secret=" + app_secret + \
              "&scope=https%3A%2F%2Fapi.botframework.com%2F.default"
    response123 = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token?client_id=" +
                             app_id + "&client_secret=" + app_secret + "&grant_type=client_credentials&"
                             "scope=https%3A%2F%2Fgraph.microsoft.com%2F.default", data=payload,
                             headers={"Host": "login.microsoftonline.com",
                                      "Content-Type": "application/x-www-form-urlencoded"})
    data123 = response123.json()
    token = data123["access_token"]
    bot = skype_chatbot.SkypeBot(app_id, app_secret)
    
    try:
        data = json.loads(request.data) 
        bot_id = data['recipient']['id']
        bot_name = data['recipient']['name']
        recipient = data['from']
        service = data['serviceUrl']
        sender = data['conversation']['id']
        replyToId=data['id']

        if data['text'] in ['選單','menu','清單'] :
            button1 = bot.create_button("openUrl","Horizon Wesite","https://www.horizonfitness.com/")
            button2 = bot.create_button("openUrl","Horizon Spec","https://docs.google.com/spreadsheets/d/1HbhwHKEyW_3Pnzp8nLMJtXNq0WtwqgsZ/edit?gid=549883299#gid=549883299")
            button3 = bot.create_button("openUrl","Horizon @Zone","https://global.horizonfitness.com/tw/zht/exercise-innovations/atzone")
            url = 'https://horizonfitness.mx/cdn/shop/files/Horizon_Fitness_logo_1_color_white_Shopi.jpg?v=1630620395'
            img1 = bot.create_card_image(url,alt="hello")
            #here in place of `hero` you can specify `thumbnail` to send thumnail card.  
            attachment1 = bot.create_card_attachment("hero","Horizon Card List",subtitle="Menu list",text="Horizon Menu",images=[img1],buttons=[button1,button2,button3])
            bot.send_card(bot_id, bot_name, recipient, replyToId,service,sender,"carousel", [attachment1],text="")# 
        else :
            #bot.send_media(bot_id, bot_name, recipient,service,sender,"carousel","https://lurvink.nl/wp-content/themes/Lurvink/img/loader.gif")
            text_gpt = chat_session.send_message(data['text'])
            text = text_gpt.text.replace('**','').replace('*','-')
            text = text.replace('\n\n','\n').replace('\n\n\n','\n').replace('\n\n\n\n','\n').rstrip('\n')
            bot.send_message(bot_id, bot_name, recipient, service, sender, text)
        
    except Exception as e:
      print(e)

    # 回傳回應給 Azure Bot Service
    return 'Code: 200'

if __name__ == "__main__":
    app.run()
