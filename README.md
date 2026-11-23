# İkinci tip qeyri-səlis AHP + TOPSIS

Dissertasiya üçün hazırladığım qərar dəstək sistemi. Sistem İT layihələrinin seçimi məsələsini interval tip-2 qeyri-səlis ədədlərlə həll edir və heç bir mərhələdə defuzzifikasiyadan istifadə etmir.

İş ardıcıllığı:

1. Ekspertlərin cüt-cüt müqayisə matrisi yüklənir.
2. Matrisin konsistentliyi yoxlanılır və matris məqbul konsistent hala gətirilir.
3. IT2 çəkilər hesablanır.
4. Alternativlər IT2 TOPSIS ilə sıralanır.
5. Nəticənin dayanıqlığı həssaslıq təhlili, rank reversal testləri və IT2-SMAA ilə yoxlanılır.

Məlumatı CSV, TXT və ya Excel faylı ilə yükləmək olar. Nümunə fayllar `examples/` qovluğundadır. İnterfeys Azərbaycan, rus və ingilis dillərindədir.

## Kompüterdə işə salmaq

```
pip install -r requirements.txt
streamlit run app.py
```
