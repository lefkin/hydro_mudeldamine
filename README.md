# Hüdroloogilise modelleerimine
Pythoni skriptid SAGA hüdroloogilise modelleerimise töövoo automatiseerimiseks jm abivahendid.

# saga_modelleerimine.py
QGis-is Pythoni konsoolis SAGA-GIS kõrgusmudelil põhineva hüdroloogilse modelleerimise läbiviimine järjekorras:

1. Kõrgusmudeli import
2. Kraavide kõrvetamine (vajadusel)
3. Neelude silumine (Fill sinks);
4. Vooluakumulatsiooni arvutamine;
5. Voolukanalite tekitamine;
6. Valgalade piiritlemine

Enne skripti käivitamist tuleb määrata 1) SAGA käivitusfaili asukoht kõvakettal; 2) töökataloog, kuhu salvestatakse modelleerimise tulemused; 3) kõrgusmudeli rasterfaili asukoht; 4) paisude vektorkiht joontena; 5) kraavide vektorkiht.

Kraavide ja paisude vektorite olemasolu ei ole kohustuslik. Kraavide vektorkiht on vajalik kraavide rõhutamiseks kõrgusmudelil, nö. kraavide sisse kõrvetamiseks. Paisude kaardikiht on vaja määrata, kui soovitakse modelleerida kraavide sulgemise mõju vooluakumulatsioonile. Paisude joontekihi tekitamiseks punktidest on eraldi abiskript dams_from_points.py .

Python faili avamisel QGis-i Python redaktoris tuleb vastavad parameetrid faili viidatud asukohtades kohandada. Faili lõpus on tuleb teha valik soovitud modelleerimise jada valimiseks.

# dams_from_points.py
Pythoni skript, mis tekitab digitud kraavidele punktide kohale etteantud pikkusega paisude joon-ruumikujud. Vajalik on kraavide joonte kiht ja paisude punktid kraavil. Paisude digimine punktidena on mugavam ja kiirem. Kui paisude kihil on väli "Pikkus", tekitatakse paisude joontekuju sellel väljal määratud pikkusega. Erineva pikkuse väärtusega punktide asukohas erineva pikkusega jooned. Paisude jooned paigutatakse konkreetsele punktile lähima kraaviga risti ja kraavi suhtes võrdselt kummalegi poole.
