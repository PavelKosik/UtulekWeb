# Tipy pro inzeráty koček na Pesweb.cz

Web si kočky bere z Peswebu, takže čím lepší je inzerát, tím rychleji kočka najde domov. Tipy vycházejí ze studií útulků (odkazy dole) a z rozboru všech 65 inzerátů depozita z října 2026.

## Jak jsou na tom inzeráty teď (18. 10. 2026)

- **45 z 65 inzerátů má jen jednu fotku**, 29 hlavních fotek je z klece nebo přepravky.
- **21 inzerátů ukazuje kočky, které už v depozitu nejsou.** U šesti z nich jsou pryč všechny kočky (Simba, Sweety, Safira a Sam, Moulík, Strašilka, Magie a Matylda). Pesweb je přitom nabízí v rámečku „Další kočky v útulku“ u všech ostatních inzerátů.
- 53 inzerátů nemá vyplněné žádné políčko „Hodí se“, očkování a čip nejsou vyplněné skoro nikde.
- 42 inzerátů má zastaralý text (věk, „dnes“, „fotky brzy přidám“).
- 23 koček čeká déle než rok. Právě ty jsou na webu nahoře v „Čekají nejdéle“, takže jejich inzeráty vidí nejvíc lidí.

## Šablona inzerátu

**Políčka**
- **Jméno:** jen jméno s velkým prvním písmenem. Ne „ZAMLUVENÁ“ ani „jako jedináček“ v názvu.
- **Jedna kočka = jeden inzerát.** Dvojice jen u koček, které musí jít spolu. Pesweb filtruje podle pohlaví a věku inzerátu, takže vrh v jednom inzerátu se ve filtrech ztratí.
- **Datum narození** vyplnit, věk do textu nepsat (za rok už nesedí).
- **Hodí se:** vyplnit všech 9 políček ano/ne.
- **Zdraví:** očkování, kastrace, čip, FIV/FeLV. Musí sedět s textem.
- **Akutní adopce:** jen s důvodem v textu, po vyřešení zrušit.

**Fotky** (5–8 kusů, denní světlo, bez blesku, z výšky kočičích očí)
1. Portrét s ostrýma očima.
2. Celá kočka.
3. Doma nebo v dočasce.
4. S hračkou, hlavně u černých a starších koček.
5. S člověkem.
6. Pravdivý detail handicapu, pokud nějaký má.

Na fotkách nemají být mříže, přepravka, misky, kočkolit, datum v rohu, screenshot z Facebooku ani jiné kočky. U koček, které čekají dlouho, fotky obnovit zhruba každé 3 měsíce.

**Text** (třetí osoba, 5–7 vět, 80–150 slov)

> [Jméno] je [barva] [kočka/kocour], nar. cca [rok]. [2–3 konkrétní projevy povahy.] [Jak se snese s dětmi, kočkami, psy.] [Byt, nebo i ven.] [Kastrace, očkování, čip, testy, léčba.] Hledá [jaký domov]. Adopce je bez poplatku, na adopční smlouvu. Tel. 607 707 537.

Do textu nepatří deník aktualizací, „dnes/zítra“, dlouhý příběh odchytu, nadávky, výzvy ke sdílení a jiné kočky. Tohle patří na Facebook.

**Po adopci** inzerát týž den stáhnout. Nedopisovat do něj „ADOPTOVANÝ“.

## Proč to funguje

- **Víc ostrých fotek, ideálně 5 až 10.** Kvalita fotky je nejsilnější známý faktor rychlosti adopce. Psi s dobrou fotkou našli domov zhruba za 14 dní, se špatnou za 43.
- **Fotit doma, ne v kleci.** Fotky koček v domácím prostředí lidé na Facebooku sdílejí zhruba třikrát víc. Proto jsou dočasky na fotky skvělé.
- **Černé a starší kočky fotit s hračkou.** Hračka na fotce zvyšuje počet prokliků a černé kočky čekají nejdéle.
- **Krátké video, 10 až 20 vteřin hraní** z mobilu, nic víc.
- **Psát ve třetí osobě** („Zina je…“, ne „Jsem Zina…“). Kočky s popisem ve třetí osobě našly domov v průměru o 2,5 dne dřív.
- **Věcně a konkrétně**: jaká je, co má ráda, co jí vadí. Méně zdrobnělin a slov jako „kamarád“ nebo „parťák“.

## Jednou za měsíc (15 minut)

Projít inzeráty starší než 3 měsíce: je kočka pořád k adopci, je fotka aktuální, sedí věk a stav? Kočky, které odešly, stáhnout.

## V nastavení útulku na Peswebu

- **Vyplnit adopční postup.** Bez něj Pesweb u poptávky ukazuje obecné kroky včetně „Zaplacení poplatku“, přitom u nás je adopce zdarma.
- **Otevírací doba:** teď je „Neuvedeno“, stačí „po domluvě“.

## Na webu

- Sekce **„Čekají nejdéle“** na webu řadí kočky podle data nálezu. U koček, které jsou tam nahoře, se nové fotky vyplatí nejvíc.
- Kočka s **„Akutní adopce“** na Peswebu jde nahoru na úvodní stránku, pokud ji uvedete v `tools/build.py` (proměnná `APPEAL`).
- Čísla „X koček našlo domov“ a „Y inzerátů“ se mění ručně v `tools/build.py` (`ADOPTED`, `LISTED`).

## Zdroje

- Lampe & Witte (2015): kvalita fotky a rychlost adopce, https://texasstandard.org/stories/glamour-shots-help-shelter-pets-find-homes-faster/
- Workman & Hoffman (2015): 892 koček, prokliky, barva srsti, hračky, https://psmag.com/social-justice/all-of-those-cat-photos-on-the-internet-are-actually-doing-some-good/
- Rix a kol. (2020): 4 460 koček, popis ve třetí osobě, https://pmc.ncbi.nlm.nih.gov/articles/PMC7823898/
- Markowitz (2020): věcné inzeráty fungují líp, https://news.uoregon.edu/content/writing-better-pet-adoption-ads-could-prevent-euthanasia
- Morrison (2024): fotky z domova se sdílejí víc, https://pmc.ncbi.nlm.nih.gov/articles/PMC11590987
