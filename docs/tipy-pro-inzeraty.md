# Tipy pro inzeráty koček na Pesweb.cz

Web si kočky bere z Peswebu, takže čím lepší je inzerát, tím rychleji kočka najde domov. Tipy vycházejí ze studií útulků (odkazy dole).

## Fotky

- **Víc ostrých fotek, ideálně 5 až 10.** Kvalita fotky je nejsilnější známý faktor rychlosti adopce. Psi s dobrou fotkou našli domov zhruba za 14 dní, se špatnou za 43.
- **Fotit doma, ne v kleci.** Fotky koček v domácím prostředí lidé na Facebooku sdílejí zhruba třikrát víc. Proto jsou dočasky na fotky skvělé.
- **Denní světlo a výška kočičích očí.** Bez blesku.
- **Černé a starší kočky fotit s hračkou.** Hračka na fotce zvyšuje počet prokliků a černé kočky čekají nejdéle.
- **Krátké video, 10 až 20 vteřin hraní** z mobilu, nic víc.

## Text

- **Psát ve třetí osobě** („Zina je…“, ne „Jsem Zina…“). Kočky s popisem ve třetí osobě našly domov v průměru o 2,5 dne dřív.
- **Věcně a konkrétně**: jaká je, co má ráda, co jí vadí. Méně zdrobnělin a slov jako „kamarád“ nebo „parťák“.
- **Nahoru jedna věta o tom, kam se hodí**: byt / dům se zahradou, děti od kolika let, jiné kočky, psi, ven / jen doma.
- **Zdraví jednou větou**: očkovaná, odčervená, testy FIV/FeLV, kastrovaná (nebo podmínka kastrace u koťat).
- **Jedna kočka = jeden inzerát.** Výjimkou jsou páry, které musí jít spolu. Vrhy rozdělit, jakmile je to možné.
- Políčka „Hodí se“ na Peswebu (k dětem, k jiné kočce, do bytu…) vyplnit u každé kočky.

## Na webu

- Sekce **„Čekají nejdéle“** na webu řadí kočky podle data nálezu. U koček, které jsou tam nahoře, se vyplatí přidat nové fotky.
- Kočka s **„Akutní adopce“** na Peswebu jde nahoru na úvodní stránku, pokud ji uvedete v `tools/build.py` (proměnná `APPEAL`).
- Čísla „X koček našlo domov“ a „Y inzerátů“ se mění ručně v `tools/build.py` (`ADOPTED`, `LISTED`).

## Zdroje

- Lampe & Witte (2015): kvalita fotky a rychlost adopce, https://texasstandard.org/stories/glamour-shots-help-shelter-pets-find-homes-faster/
- Workman & Hoffman (2015): 892 koček, prokliky, barva srsti, hračky, https://psmag.com/social-justice/all-of-those-cat-photos-on-the-internet-are-actually-doing-some-good/
- Rix a kol. (2020): 4 460 koček, popis ve třetí osobě, https://pmc.ncbi.nlm.nih.gov/articles/PMC7823898/
- Markowitz (2020): věcné inzeráty fungují líp, https://news.uoregon.edu/content/writing-better-pet-adoption-ads-could-prevent-euthanasia
- Morrison (2024): fotky z domova se sdílejí víc, https://pmc.ncbi.nlm.nih.gov/articles/PMC11590987
