#!/usr/bin/env python3
"""
Euskera A1 Podcast Generator
Genera podcasts MP3 para cada leccion del curso de euskera A1
usando edge-tts (Microsoft Azure TTS gratuito).

Uso:
    python generate_podcast.py --lesson 1      # Genera podcast de leccion 1
    python generate_podcast.py --all           # Genera todos los podcasts
    python generate_podcast.py --list          # Lista lecciones disponibles
"""

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import edge_tts
except ImportError:
    print("Error: edge-tts no esta instalado.")
    print("Instala con: pip install edge-tts")
    sys.exit(1)

# Intentar importar tqdm para progress bar
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Nota: tqdm no instalado. Sin barra de progreso.")
    print("Puedes instalarlo con: pip install tqdm")

# Intentar importar pydub para combinar audio
try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("Error: pydub no esta instalado.")
    print("Instala con: pip install pydub")
    print("Tambien necesitas ffmpeg instalado en el sistema.")
    sys.exit(1)


# ============================================================================
# CONFIGURACION
# ============================================================================

# Voces de edge-tts
VOICE_EUSKERA = "eu-ES-AnderNeural"      # Voz para euskera
VOICE_SPANISH = "es-ES-AlvaroNeural"      # Voz para explicaciones en castellano

# Velocidad reducida para mejor comprension A1 (-5%)
RATE_ADJUSTMENT = "-5%"

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent
PODCASTS_DIR = BASE_DIR / "podcasts"


# ============================================================================
# SCRIPTS DE CADA LECCION
# ============================================================================

LESSON_SCRIPTS = {
    1: {
        "title": "Kaixo! Aurkezpenak",
        "title_es": "Hola! Presentaciones",
        "segments": [
            # Introduccion
            ("eu", "Kaixo! Ongi etorri euskara ikastarora."),
            ("es", "Hola, bienvenido al curso de euskera. En esta primera leccion aprenderemos a saludarnos y presentarnos en euskera."),

            # Saludos
            ("es", "Empecemos con los saludos basicos en euskera."),
            ("eu", "Agurrak."),
            ("eu", "Kaixo."),
            ("es", "Kaixo significa hola. Es informal y se usa en cualquier momento."),
            ("eu", "Egun on."),
            ("es", "Egun on significa buenos dias. Se usa por la manana."),
            ("eu", "Arratsalde on."),
            ("es", "Arratsalde on significa buenas tardes."),
            ("eu", "Gabon."),
            ("es", "Gabon significa buenas noches."),
            ("eu", "Agur."),
            ("es", "Agur significa adios."),
            ("eu", "Gero arte."),
            ("es", "Gero arte significa hasta luego."),

            # Pronunciacion
            ("es", "Repitamos los saludos juntos."),
            ("eu", "Kaixo. Egun on. Arratsalde on. Gabon. Agur. Gero arte."),

            # Pronombres
            ("es", "Ahora veamos los pronombres personales, que son muy importantes."),
            ("eu", "Izenordain pertsonalak."),
            ("eu", "Ni."),
            ("es", "Ni significa yo."),
            ("eu", "Zu."),
            ("es", "Zu significa tu."),
            ("eu", "Bera."),
            ("es", "Bera significa el o ella."),
            ("eu", "Gu."),
            ("es", "Gu significa nosotros o nosotras."),
            ("eu", "Zuek."),
            ("es", "Zuek significa vosotros o vosotras."),
            ("eu", "Haiek."),
            ("es", "Haiek significa ellos o ellas."),

            # Verbo IZAN
            ("es", "El verbo mas importante del euskera es izan, que significa ser o estar."),
            ("eu", "Izan aditza."),
            ("eu", "Ni naiz."),
            ("es", "Ni naiz. Yo soy."),
            ("eu", "Zu zara."),
            ("es", "Zu zara. Tu eres."),
            ("eu", "Bera da."),
            ("es", "Bera da. El o ella es."),
            ("eu", "Gu gara."),
            ("es", "Gu gara. Nosotros somos."),
            ("eu", "Zuek zarete."),
            ("es", "Zuek zarete. Vosotros sois."),
            ("eu", "Haiek dira."),
            ("es", "Haiek dira. Ellos son."),

            # Ejemplos de presentacion
            ("es", "Veamos como presentarnos."),
            ("eu", "Ni Ander naiz."),
            ("es", "Ni Ander naiz significa yo soy Ander."),
            ("eu", "Ni ikaslea naiz."),
            ("es", "Ni ikaslea naiz significa yo soy estudiante."),
            ("eu", "Ni Madrilgoa naiz."),
            ("es", "Ni Madrilgoa naiz significa yo soy de Madrid."),

            # Preguntas basicas
            ("es", "Ahora algunas preguntas utiles."),
            ("eu", "Nor zara?"),
            ("es", "Nor zara significa quien eres."),
            ("eu", "Nongoa zara?"),
            ("es", "Nongoa zara significa de donde eres."),
            ("eu", "Zer moduz?"),
            ("es", "Zer moduz significa que tal."),
            ("eu", "Nola zaude?"),
            ("es", "Nola zaude significa como estas."),

            # Respuestas
            ("eu", "Ondo, eskerrik asko."),
            ("es", "Ondo, eskerrik asko significa bien, muchas gracias."),

            # Numeros
            ("es", "Terminemos con los numeros del cero al diez."),
            ("eu", "Zenbakiak."),
            ("eu", "Zero. Bat. Bi. Hiru. Lau. Bost. Sei. Zazpi. Zortzi. Bederatzi. Hamar."),
            ("es", "Cero, uno, dos, tres, cuatro, cinco, seis, siete, ocho, nueve, diez."),

            # Repaso final
            ("es", "Repasemos lo mas importante de esta leccion."),
            ("eu", "Kaixo! Ni Ander naiz. Ikaslea naiz. Ondo nago, eskerrik asko. Agur!"),
            ("es", "Hola! Soy Ander. Soy estudiante. Estoy bien, muchas gracias. Adios!"),
            ("es", "Muy bien! Has completado la primera leccion. Practica estos saludos y presentaciones todos los dias. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    2: {
        "title": "Familia",
        "title_es": "La familia",
        "segments": [
            ("eu", "Kaixo! Ongi etorri bigarren ikasgaira."),
            ("es", "Hola, bienvenido a la segunda leccion. Hoy aprenderemos el vocabulario de la familia en euskera."),

            # Familia nuclear
            ("es", "Empecemos con la familia nuclear."),
            ("eu", "Familia."),
            ("eu", "Aita."),
            ("es", "Aita significa padre."),
            ("eu", "Ama."),
            ("es", "Ama significa madre."),
            ("eu", "Semea."),
            ("es", "Semea significa hijo."),
            ("eu", "Alaba."),
            ("es", "Alaba significa hija."),
            ("eu", "Anaia."),
            ("es", "Anaia significa hermano."),
            ("eu", "Arreba."),
            ("es", "Arreba significa hermana, cuando lo dice un hombre."),
            ("eu", "Ahizpa."),
            ("es", "Ahizpa significa hermana, cuando lo dice una mujer."),
            ("eu", "Neba."),
            ("es", "Neba significa hermano, cuando lo dice una mujer."),

            # Familia extendida
            ("es", "Ahora la familia extendida."),
            ("eu", "Aitona."),
            ("es", "Aitona significa abuelo."),
            ("eu", "Amona."),
            ("es", "Amona significa abuela."),
            ("eu", "Osaba."),
            ("es", "Osaba significa tio."),
            ("eu", "Izeba."),
            ("es", "Izeba significa tia."),
            ("eu", "Lehengusua."),
            ("es", "Lehengusua significa primo o prima."),
            ("eu", "Iloba."),
            ("es", "Iloba significa sobrino, sobrina o nieto, nieta."),

            # Posesivos
            ("es", "Para hablar de nuestra familia usamos los posesivos."),
            ("eu", "Nire aita."),
            ("es", "Nire aita significa mi padre."),
            ("eu", "Zure ama."),
            ("es", "Zure ama significa tu madre."),
            ("eu", "Bere anaia."),
            ("es", "Bere anaia significa su hermano."),
            ("eu", "Gure familia."),
            ("es", "Gure familia significa nuestra familia."),

            # Ejemplos
            ("es", "Veamos algunas frases utiles."),
            ("eu", "Nire aita Mikel da."),
            ("es", "Nire aita Mikel da significa mi padre es Mikel."),
            ("eu", "Nire ama Miren da."),
            ("es", "Nire ama Miren da significa mi madre es Miren."),
            ("eu", "Bi anaia ditut."),
            ("es", "Bi anaia ditut significa tengo dos hermanos."),
            ("eu", "Anaia bat eta arreba bat ditut."),
            ("es", "Anaia bat eta arreba bat ditut significa tengo un hermano y una hermana."),

            # Preguntas
            ("es", "Preguntas sobre la familia."),
            ("eu", "Anaiarik baduzu?"),
            ("es", "Anaiarik baduzu significa tienes hermanos."),
            ("eu", "Semerik baduzu?"),
            ("es", "Semerik baduzu significa tienes hijos."),
            ("eu", "Zenbat anaia dituzu?"),
            ("es", "Zenbat anaia dituzu significa cuantos hermanos tienes."),

            # Numeros 11-20
            ("es", "Aprendamos los numeros del once al veinte."),
            ("eu", "Hamaika. Hamabi. Hamahiru. Hamalau. Hamabost. Hamasei. Hamazazpi. Hemezortzi. Hemeretzi. Hogei."),
            ("es", "Once, doce, trece, catorce, quince, dieciseis, diecisiete, dieciocho, diecinueve, veinte."),

            # Repaso
            ("es", "Repasemos la familia."),
            ("eu", "Aita, ama, semea, alaba, anaia, arreba, aitona, amona."),
            ("eu", "Nire familia handia da. Bi anaia eta arreba bat ditut."),
            ("es", "Mi familia es grande. Tengo dos hermanos y una hermana."),
            ("es", "Excelente! Has completado la leccion sobre la familia. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    3: {
        "title": "Koloreak eta Zenbakiak",
        "title_es": "Colores y Numeros",
        "segments": [
            ("eu", "Kaixo! Ongi etorri hirugarren ikasgaira."),
            ("es", "Hola, bienvenido a la tercera leccion. Hoy aprenderemos los colores y mas numeros en euskera."),

            # Colores
            ("es", "Empecemos con los colores basicos."),
            ("eu", "Koloreak."),
            ("eu", "Gorria."),
            ("es", "Gorria significa rojo."),
            ("eu", "Urdina."),
            ("es", "Urdina significa azul."),
            ("eu", "Berdea."),
            ("es", "Berdea significa verde."),
            ("eu", "Horia."),
            ("es", "Horia significa amarillo."),
            ("eu", "Zuria."),
            ("es", "Zuria significa blanco."),
            ("eu", "Beltza."),
            ("es", "Beltza significa negro."),
            ("eu", "Laranja."),
            ("es", "Laranja significa naranja."),
            ("eu", "Morea."),
            ("es", "Morea significa morado."),
            ("eu", "Arrosa."),
            ("es", "Arrosa significa rosa."),
            ("eu", "Marroia."),
            ("es", "Marroia significa marron."),
            ("eu", "Grisa."),
            ("es", "Grisa significa gris."),

            # Uso de colores
            ("es", "En euskera, el color va despues del sustantivo y termina en a."),
            ("eu", "Etxe gorria."),
            ("es", "Etxe gorria significa la casa roja."),
            ("eu", "Auto urdina."),
            ("es", "Auto urdina significa el coche azul."),
            ("eu", "Sagar berdea."),
            ("es", "Sagar berdea significa la manzana verde."),

            # Numeros 20-100
            ("es", "Ahora aprendamos los numeros del veinte al cien."),
            ("eu", "Hogei."),
            ("es", "Hogei es veinte."),
            ("eu", "Hogeita bat."),
            ("es", "Hogeita bat es veintiuno."),
            ("eu", "Hogeita hamar."),
            ("es", "Hogeita hamar es treinta."),
            ("eu", "Berrogei."),
            ("es", "Berrogei es cuarenta."),
            ("eu", "Berrogeita hamar."),
            ("es", "Berrogeita hamar es cincuenta."),
            ("eu", "Hirurogei."),
            ("es", "Hirurogei es sesenta."),
            ("eu", "Hirurogeita hamar."),
            ("es", "Hirurogeita hamar es setenta."),
            ("eu", "Laurogei."),
            ("es", "Laurogei es ochenta."),
            ("eu", "Laurogeita hamar."),
            ("es", "Laurogeita hamar es noventa."),
            ("eu", "Ehun."),
            ("es", "Ehun es cien."),

            # Preguntas con colores
            ("es", "Preguntas utiles con colores."),
            ("eu", "Zer kolore da?"),
            ("es", "Zer kolore da significa de que color es."),
            ("eu", "Gorria da."),
            ("es", "Gorria da significa es rojo."),
            ("eu", "Zein da zure kolore gogokoena?"),
            ("es", "Zein da zure kolore gogokoena significa cual es tu color favorito."),
            ("eu", "Nire kolore gogokoena urdina da."),
            ("es", "Mi color favorito es el azul."),

            # Repaso
            ("es", "Repasemos los colores."),
            ("eu", "Gorria, urdina, berdea, horia, zuria, beltza."),
            ("es", "Rojo, azul, verde, amarillo, blanco, negro."),
            ("es", "Muy bien! Has aprendido los colores y numeros. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    4: {
        "title": "Gorputza",
        "title_es": "El cuerpo humano",
        "segments": [
            ("eu", "Kaixo! Ongi etorri laugarren ikasgaira."),
            ("es", "Hola, bienvenido a la cuarta leccion. Hoy aprenderemos las partes del cuerpo en euskera."),

            # Cabeza
            ("es", "Empecemos con la cabeza."),
            ("eu", "Gorputza."),
            ("eu", "Burua."),
            ("es", "Burua significa cabeza."),
            ("eu", "Aurpegia."),
            ("es", "Aurpegia significa cara."),
            ("eu", "Begiak."),
            ("es", "Begiak significa ojos."),
            ("eu", "Belarriak."),
            ("es", "Belarriak significa orejas."),
            ("eu", "Sudurra."),
            ("es", "Sudurra significa nariz."),
            ("eu", "Ahoa."),
            ("es", "Ahoa significa boca."),
            ("eu", "Hortzak."),
            ("es", "Hortzak significa dientes."),
            ("eu", "Ilea."),
            ("es", "Ilea significa pelo."),

            # Cuerpo
            ("es", "Ahora el resto del cuerpo."),
            ("eu", "Lepoa."),
            ("es", "Lepoa significa cuello."),
            ("eu", "Sorbalda."),
            ("es", "Sorbalda significa hombro."),
            ("eu", "Besoa."),
            ("es", "Besoa significa brazo."),
            ("eu", "Eskua."),
            ("es", "Eskua significa mano."),
            ("eu", "Hatzak."),
            ("es", "Hatzak significa dedos."),
            ("eu", "Bizkarra."),
            ("es", "Bizkarra significa espalda."),
            ("eu", "Sabela."),
            ("es", "Sabela significa barriga."),
            ("eu", "Hanka."),
            ("es", "Hanka significa pierna."),
            ("eu", "Oina."),
            ("es", "Oina significa pie."),
            ("eu", "Belaunna."),
            ("es", "Belauna significa rodilla."),

            # Verbo EDUKI (tener)
            ("es", "Para describir el cuerpo usamos el verbo eduki, que significa tener."),
            ("eu", "Bi begi ditut."),
            ("es", "Bi begi ditut significa tengo dos ojos."),
            ("eu", "Bi esku ditut."),
            ("es", "Tengo dos manos."),
            ("eu", "Hamar hatz ditut."),
            ("es", "Tengo diez dedos."),

            # Adjetivos
            ("es", "Algunos adjetivos para describir."),
            ("eu", "Handia."),
            ("es", "Handia significa grande."),
            ("eu", "Txikia."),
            ("es", "Txikia significa pequeno."),
            ("eu", "Luzea."),
            ("es", "Luzea significa largo."),
            ("eu", "Laburra."),
            ("es", "Laburra significa corto."),

            # Ejemplos
            ("eu", "Nire ilea beltza da."),
            ("es", "Mi pelo es negro."),
            ("eu", "Nire begiak marroiak dira."),
            ("es", "Mis ojos son marrones."),
            ("eu", "Sudur handia dut."),
            ("es", "Tengo la nariz grande."),

            # Repaso
            ("es", "Repasemos las partes del cuerpo."),
            ("eu", "Burua, begiak, sudurra, ahoa, belarriak, eskuak, hankak."),
            ("es", "Cabeza, ojos, nariz, boca, orejas, manos, piernas."),
            ("es", "Excelente! Has aprendido las partes del cuerpo. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    5: {
        "title": "Janaria",
        "title_es": "La comida",
        "segments": [
            ("eu", "Kaixo! Ongi etorri bosgarren ikasgaira."),
            ("es", "Hola, bienvenido a la quinta leccion. Hoy aprenderemos vocabulario sobre la comida en euskera."),

            # Comidas del dia
            ("es", "Empecemos con las comidas del dia."),
            ("eu", "Janaria."),
            ("eu", "Gosaria."),
            ("es", "Gosaria significa desayuno."),
            ("eu", "Bazkaria."),
            ("es", "Bazkaria significa almuerzo o comida."),
            ("eu", "Afaria."),
            ("es", "Afaria significa cena."),

            # Alimentos basicos
            ("es", "Alimentos basicos."),
            ("eu", "Ogia."),
            ("es", "Ogia significa pan."),
            ("eu", "Ura."),
            ("es", "Ura significa agua."),
            ("eu", "Esnea."),
            ("es", "Esnea significa leche."),
            ("eu", "Kafea."),
            ("es", "Kafea significa cafe."),
            ("eu", "Tea."),
            ("es", "Tea significa te."),
            ("eu", "Arrautza."),
            ("es", "Arrautza significa huevo."),
            ("eu", "Gazta."),
            ("es", "Gazta significa queso."),
            ("eu", "Urdaiazpikoa."),
            ("es", "Urdaiazpikoa significa jamon."),

            # Frutas
            ("es", "Frutas."),
            ("eu", "Frutak."),
            ("eu", "Sagarra."),
            ("es", "Sagarra significa manzana."),
            ("eu", "Laranja."),
            ("es", "Laranja significa naranja."),
            ("eu", "Platanoa."),
            ("es", "Platanoa significa platano."),
            ("eu", "Marrubiak."),
            ("es", "Marrubiak significa fresas."),

            # Verduras
            ("es", "Verduras."),
            ("eu", "Barazkiak."),
            ("eu", "Tomatea."),
            ("es", "Tomatea significa tomate."),
            ("eu", "Letxuga."),
            ("es", "Letxuga significa lechuga."),
            ("eu", "Patata."),
            ("es", "Patata significa patata."),
            ("eu", "Tipula."),
            ("es", "Tipula significa cebolla."),

            # Carne y pescado
            ("es", "Carne y pescado."),
            ("eu", "Haragia."),
            ("es", "Haragia significa carne."),
            ("eu", "Oilaskoa."),
            ("es", "Oilaskoa significa pollo."),
            ("eu", "Arraina."),
            ("es", "Arraina significa pescado."),

            # Verbos
            ("es", "Verbos relacionados con la comida."),
            ("eu", "Jan."),
            ("es", "Jan significa comer."),
            ("eu", "Edan."),
            ("es", "Edan significa beber."),
            ("eu", "Nahi."),
            ("es", "Nahi significa querer."),
            ("eu", "Gose naiz."),
            ("es", "Gose naiz significa tengo hambre."),
            ("eu", "Egarri naiz."),
            ("es", "Egarri naiz significa tengo sed."),

            # Frases utiles
            ("es", "Frases utiles en un restaurante."),
            ("eu", "Ura, mesedez."),
            ("es", "Agua, por favor."),
            ("eu", "Ogia nahi dut."),
            ("es", "Quiero pan."),
            ("eu", "Kafe bat, mesedez."),
            ("es", "Un cafe, por favor."),
            ("eu", "Oso goxoa!"),
            ("es", "Muy rico!"),
            ("eu", "Kontua, mesedez."),
            ("es", "La cuenta, por favor."),

            # Repaso
            ("es", "Repasemos la comida."),
            ("eu", "Gosaria, bazkaria, afaria. Ogia, ura, kafea, sagarra."),
            ("es", "Desayuno, almuerzo, cena. Pan, agua, cafe, manzana."),
            ("es", "Muy bien! Has aprendido vocabulario de comida. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    6: {
        "title": "Etxea",
        "title_es": "La casa",
        "segments": [
            ("eu", "Kaixo! Ongi etorri seigarren ikasgaira."),
            ("es", "Hola, bienvenido a la sexta leccion. Hoy aprenderemos las partes de la casa en euskera."),

            # Partes de la casa
            ("es", "Las partes de la casa."),
            ("eu", "Etxea."),
            ("eu", "Egongela."),
            ("es", "Egongela significa salon o sala de estar."),
            ("eu", "Sukaldea."),
            ("es", "Sukaldea significa cocina."),
            ("eu", "Logela."),
            ("es", "Logela significa dormitorio."),
            ("eu", "Komuna."),
            ("es", "Komuna significa bano."),
            ("eu", "Jangela."),
            ("es", "Jangela significa comedor."),
            ("eu", "Garajea."),
            ("es", "Garajea significa garaje."),
            ("eu", "Lorategia."),
            ("es", "Lorategia significa jardin."),
            ("eu", "Balkoia."),
            ("es", "Balkoia significa balcon."),
            ("eu", "Teilatua."),
            ("es", "Teilatua significa tejado."),
            ("eu", "Eskailerak."),
            ("es", "Eskailerak significa escaleras."),

            # Muebles
            ("es", "Los muebles."),
            ("eu", "Altzariak."),
            ("eu", "Ohea."),
            ("es", "Ohea significa cama."),
            ("eu", "Mahaia."),
            ("es", "Mahaia significa mesa."),
            ("eu", "Aulkia."),
            ("es", "Aulkia significa silla."),
            ("eu", "Sofa."),
            ("es", "Sofa significa sofa."),
            ("eu", "Armairua."),
            ("es", "Armairua significa armario."),
            ("eu", "Ispilua."),
            ("es", "Ispilua significa espejo."),
            ("eu", "Telebista."),
            ("es", "Telebista significa television."),

            # EGON (estar)
            ("es", "El verbo egon significa estar ubicado."),
            ("eu", "Sukaldean nago."),
            ("es", "Estoy en la cocina."),
            ("eu", "Logelan dago."),
            ("es", "Esta en el dormitorio."),
            ("eu", "Non dago?"),
            ("es", "Non dago significa donde esta."),

            # Locativos
            ("es", "Palabras de ubicacion."),
            ("eu", "Gainean."),
            ("es", "Gainean significa encima."),
            ("eu", "Azpian."),
            ("es", "Azpian significa debajo."),
            ("eu", "Ondoan."),
            ("es", "Ondoan significa al lado."),
            ("eu", "Barruan."),
            ("es", "Barruan significa dentro."),
            ("eu", "Kanpoan."),
            ("es", "Kanpoan significa fuera."),

            # Ejemplos
            ("eu", "Liburua mahaiaren gainean dago."),
            ("es", "El libro esta encima de la mesa."),
            ("eu", "Katua sofaren azpian dago."),
            ("es", "El gato esta debajo del sofa."),

            # Repaso
            ("es", "Repasemos las partes de la casa."),
            ("eu", "Egongela, sukaldea, logela, komuna, jangela."),
            ("es", "Salon, cocina, dormitorio, bano, comedor."),
            ("es", "Excelente! Has aprendido la casa. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    7: {
        "title": "Lanbideak",
        "title_es": "Las profesiones",
        "segments": [
            ("eu", "Kaixo! Ongi etorri zazpigarren ikasgaira."),
            ("es", "Hola, bienvenido a la septima leccion. Hoy aprenderemos las profesiones en euskera."),

            # Profesiones
            ("es", "Las profesiones basicas."),
            ("eu", "Lanbideak."),
            ("eu", "Irakaslea."),
            ("es", "Irakaslea significa profesor o profesora."),
            ("eu", "Ikaslea."),
            ("es", "Ikaslea significa estudiante."),
            ("eu", "Medikua."),
            ("es", "Medikua significa medico o medica."),
            ("eu", "Erizaina."),
            ("es", "Erizaina significa enfermero o enfermera."),
            ("eu", "Abokatua."),
            ("es", "Abokatua significa abogado o abogada."),
            ("eu", "Ingeniaritza."),
            ("es", "Ingeniaritza significa ingeniero o ingeniera."),
            ("eu", "Arkitektoa."),
            ("es", "Arkitektoa significa arquitecto o arquitecta."),
            ("eu", "Sukaldaria."),
            ("es", "Sukaldaria significa cocinero o cocinera."),
            ("eu", "Gidaria."),
            ("es", "Gidaria significa conductor o conductora."),
            ("eu", "Saltzailea."),
            ("es", "Saltzailea significa vendedor o vendedora."),
            ("eu", "Kazetaria."),
            ("es", "Kazetaria significa periodista."),
            ("eu", "Polizia."),
            ("es", "Polizia significa policia."),
            ("eu", "Suhiltzailea."),
            ("es", "Suhiltzailea significa bombero o bombera."),
            ("eu", "Nekazaria."),
            ("es", "Nekazaria significa agricultor o agricultora."),

            # Lugar de trabajo
            ("es", "Donde trabajamos."),
            ("eu", "Non lan egiten duzu?"),
            ("es", "Non lan egiten duzu significa donde trabajas."),
            ("eu", "Ospitalean lan egiten dut."),
            ("es", "Trabajo en el hospital."),
            ("eu", "Eskolan lan egiten dut."),
            ("es", "Trabajo en la escuela."),
            ("eu", "Bulegoan lan egiten dut."),
            ("es", "Trabajo en la oficina."),

            # Preguntas
            ("eu", "Zer zara zu?"),
            ("es", "Que eres tu? O cual es tu profesion."),
            ("eu", "Zein da zure lanbidea?"),
            ("es", "Cual es tu profesion."),
            ("eu", "Medikua naiz."),
            ("es", "Soy medico."),
            ("eu", "Irakaslea naiz eskola batean."),
            ("es", "Soy profesor en una escuela."),

            # Dias de la semana
            ("es", "Los dias de la semana."),
            ("eu", "Asteko egunak."),
            ("eu", "Astelehena."),
            ("es", "Lunes."),
            ("eu", "Asteartea."),
            ("es", "Martes."),
            ("eu", "Asteazkena."),
            ("es", "Miercoles."),
            ("eu", "Osteguna."),
            ("es", "Jueves."),
            ("eu", "Ostirala."),
            ("es", "Viernes."),
            ("eu", "Larunbata."),
            ("es", "Sabado."),
            ("eu", "Igandea."),
            ("es", "Domingo."),

            # Repaso
            ("es", "Repasemos las profesiones."),
            ("eu", "Irakaslea, medikua, erizaina, abokatua, sukaldaria."),
            ("es", "Profesor, medico, enfermero, abogado, cocinero."),
            ("es", "Muy bien! Has aprendido las profesiones. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    8: {
        "title": "Hiria eta Garraioak",
        "title_es": "La ciudad y transportes",
        "segments": [
            ("eu", "Kaixo! Ongi etorri zortzigarren ikasgaira."),
            ("es", "Hola, bienvenido a la octava leccion. Hoy aprenderemos la ciudad y los transportes en euskera."),

            # Lugares de la ciudad
            ("es", "Lugares de la ciudad."),
            ("eu", "Hiria."),
            ("eu", "Kalea."),
            ("es", "Kalea significa calle."),
            ("eu", "Plaza."),
            ("es", "Plaza significa plaza."),
            ("eu", "Denda."),
            ("es", "Denda significa tienda."),
            ("eu", "Jatetxea."),
            ("es", "Jatetxea significa restaurante."),
            ("eu", "Ospitalea."),
            ("es", "Ospitalea significa hospital."),
            ("eu", "Bankua."),
            ("es", "Bankua significa banco."),
            ("eu", "Farmazia."),
            ("es", "Farmazia significa farmacia."),
            ("eu", "Supermerkatua."),
            ("es", "Supermerkatua significa supermercado."),
            ("eu", "Geltokia."),
            ("es", "Geltokia significa estacion."),
            ("eu", "Aireportua."),
            ("es", "Aireportua significa aeropuerto."),
            ("eu", "Parkea."),
            ("es", "Parkea significa parque."),
            ("eu", "Museoa."),
            ("es", "Museoa significa museo."),
            ("eu", "Zinema."),
            ("es", "Zinema significa cine."),

            # Transportes
            ("es", "Los transportes."),
            ("eu", "Garraioak."),
            ("eu", "Autobusa."),
            ("es", "Autobusa significa autobus."),
            ("eu", "Trena."),
            ("es", "Trena significa tren."),
            ("eu", "Metroa."),
            ("es", "Metroa significa metro."),
            ("eu", "Taxia."),
            ("es", "Taxia significa taxi."),
            ("eu", "Autoa."),
            ("es", "Autoa significa coche."),
            ("eu", "Bizikleta."),
            ("es", "Bizikleta significa bicicleta."),
            ("eu", "Hegazkina."),
            ("es", "Hegazkina significa avion."),
            ("eu", "Itsasontzia."),
            ("es", "Itsasontzia significa barco."),

            # Direcciones
            ("es", "Preguntar direcciones."),
            ("eu", "Non dago?"),
            ("es", "Donde esta."),
            ("eu", "Nola joaten naiz?"),
            ("es", "Como voy."),
            ("eu", "Barkatu, non dago geltokia?"),
            ("es", "Perdona, donde esta la estacion."),
            ("eu", "Zuzenean."),
            ("es", "Recto."),
            ("eu", "Eskuinera."),
            ("es", "A la derecha."),
            ("eu", "Ezkerrera."),
            ("es", "A la izquierda."),
            ("eu", "Hurbil."),
            ("es", "Cerca."),
            ("eu", "Urrun."),
            ("es", "Lejos."),

            # Ejemplos
            ("eu", "Museoa plazaren ondoan dago."),
            ("es", "El museo esta al lado de la plaza."),
            ("eu", "Autobusez joaten naiz lanera."),
            ("es", "Voy al trabajo en autobus."),

            # Repaso
            ("es", "Repasemos la ciudad y transportes."),
            ("eu", "Kalea, denda, jatetxea, geltokia. Autobusa, trena, autoa."),
            ("es", "Calle, tienda, restaurante, estacion. Autobus, tren, coche."),
            ("es", "Excelente! Has aprendido la ciudad. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    9: {
        "title": "Eguraldia eta Urtaroak",
        "title_es": "El clima y las estaciones",
        "segments": [
            ("eu", "Kaixo! Ongi etorri bederatzigarren ikasgaira."),
            ("es", "Hola, bienvenido a la novena leccion. Hoy aprenderemos el clima y las estaciones en euskera."),

            # Estaciones
            ("es", "Las cuatro estaciones."),
            ("eu", "Urtaroak."),
            ("eu", "Udaberria."),
            ("es", "Udaberria significa primavera."),
            ("eu", "Uda."),
            ("es", "Uda significa verano."),
            ("eu", "Udazkena."),
            ("es", "Udazkena significa otono."),
            ("eu", "Negua."),
            ("es", "Negua significa invierno."),

            # Meses
            ("es", "Los meses del ano."),
            ("eu", "Hilabeteak."),
            ("eu", "Urtarrila."),
            ("es", "Enero."),
            ("eu", "Otsaila."),
            ("es", "Febrero."),
            ("eu", "Martxoa."),
            ("es", "Marzo."),
            ("eu", "Apirila."),
            ("es", "Abril."),
            ("eu", "Maiatza."),
            ("es", "Mayo."),
            ("eu", "Ekaina."),
            ("es", "Junio."),
            ("eu", "Uztaila."),
            ("es", "Julio."),
            ("eu", "Abuztua."),
            ("es", "Agosto."),
            ("eu", "Iraila."),
            ("es", "Septiembre."),
            ("eu", "Urria."),
            ("es", "Octubre."),
            ("eu", "Azaroa."),
            ("es", "Noviembre."),
            ("eu", "Abendua."),
            ("es", "Diciembre."),

            # Clima
            ("es", "El tiempo atmosferico."),
            ("eu", "Eguraldia."),
            ("eu", "Eguzkia."),
            ("es", "Eguzkia significa sol."),
            ("eu", "Hodeia."),
            ("es", "Hodeia significa nube."),
            ("eu", "Euria."),
            ("es", "Euria significa lluvia."),
            ("eu", "Elurra."),
            ("es", "Elurra significa nieve."),
            ("eu", "Haizea."),
            ("es", "Haizea significa viento."),
            ("eu", "Tximista."),
            ("es", "Tximista significa rayo."),
            ("eu", "Trumoia."),
            ("es", "Trumoia significa trueno."),

            # Expresiones del tiempo
            ("es", "Expresiones sobre el tiempo."),
            ("eu", "Zer eguraldi egiten du?"),
            ("es", "Que tiempo hace."),
            ("eu", "Eguzki egiten du."),
            ("es", "Hace sol."),
            ("eu", "Euria ari du."),
            ("es", "Esta lloviendo."),
            ("eu", "Elurra ari du."),
            ("es", "Esta nevando."),
            ("eu", "Hotza dago."),
            ("es", "Hace frio."),
            ("eu", "Beroa dago."),
            ("es", "Hace calor."),
            ("eu", "Haize egiten du."),
            ("es", "Hace viento."),

            # Temperaturas
            ("eu", "Gaur hogeita bost gradu daude."),
            ("es", "Hoy hay veinticinco grados."),
            ("eu", "Atzo euria egin zuen."),
            ("es", "Ayer llovio."),
            ("eu", "Bihar eguzki egingo du."),
            ("es", "Manana hara sol."),

            # Repaso
            ("es", "Repasemos el clima y las estaciones."),
            ("eu", "Udaberria, uda, udazkena, negua. Eguzkia, euria, elurra."),
            ("es", "Primavera, verano, otono, invierno. Sol, lluvia, nieve."),
            ("es", "Muy bien! Has aprendido el clima. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    10: {
        "title": "Aisia eta Kirolak",
        "title_es": "Ocio y deportes",
        "segments": [
            ("eu", "Kaixo! Ongi etorri hamargarren ikasgaira."),
            ("es", "Hola, bienvenido a la decima leccion. Hoy aprenderemos ocio y deportes en euskera."),

            # Deportes
            ("es", "Los deportes."),
            ("eu", "Kirolak."),
            ("eu", "Futbola."),
            ("es", "Futbola significa futbol."),
            ("eu", "Saskibaloia."),
            ("es", "Saskibaloia significa baloncesto."),
            ("eu", "Tenisa."),
            ("es", "Tenisa significa tenis."),
            ("eu", "Igeria."),
            ("es", "Igeria significa natacion."),
            ("eu", "Korrika."),
            ("es", "Korrika significa correr."),
            ("eu", "Txirrindularitza."),
            ("es", "Txirrindularitza significa ciclismo."),
            ("eu", "Eskia."),
            ("es", "Eskia significa esqui."),
            ("eu", "Surfa."),
            ("es", "Surfa significa surf."),
            ("eu", "Mendizaletasuna."),
            ("es", "Mendizaletasuna significa montanismo."),
            ("eu", "Pelota."),
            ("es", "Pelota significa pelota vasca."),

            # Actividades de ocio
            ("es", "Actividades de ocio."),
            ("eu", "Aisia."),
            ("eu", "Irakurtzea."),
            ("es", "Irakurtzea significa leer."),
            ("eu", "Musika entzutea."),
            ("es", "Escuchar musica."),
            ("eu", "Zinera joatea."),
            ("es", "Ir al cine."),
            ("eu", "Bidaiatzea."),
            ("es", "Bidaiatzea significa viajar."),
            ("eu", "Argazkiak ateratzea."),
            ("es", "Hacer fotos."),
            ("eu", "Sukaldatzea."),
            ("es", "Sukaldatzea significa cocinar."),
            ("eu", "Marraztea."),
            ("es", "Marraztea significa dibujar."),
            ("eu", "Dantzatzea."),
            ("es", "Dantzatzea significa bailar."),

            # Gustos GUSTUKO
            ("es", "Para expresar gustos usamos gustuko."),
            ("eu", "Gustuko dut."),
            ("es", "Gustuko dut significa me gusta."),
            ("eu", "Ez dut gustuko."),
            ("es", "No me gusta."),
            ("eu", "Zer da zure gustukoa?"),
            ("es", "Que te gusta."),
            ("eu", "Futbola gustuko dut."),
            ("es", "Me gusta el futbol."),
            ("eu", "Irakurtzea asko gustuko dut."),
            ("es", "Me gusta mucho leer."),

            # Frecuencia
            ("es", "Expresiones de frecuencia."),
            ("eu", "Beti."),
            ("es", "Siempre."),
            ("eu", "Askotan."),
            ("es", "A menudo."),
            ("eu", "Batzuetan."),
            ("es", "A veces."),
            ("eu", "Gutxitan."),
            ("es", "Pocas veces."),
            ("eu", "Inoiz ez."),
            ("es", "Nunca."),

            # Ejemplos
            ("eu", "Astean hiru aldiz korrika egiten dut."),
            ("es", "Corro tres veces a la semana."),
            ("eu", "Asteburuetan mendira joaten naiz."),
            ("es", "Los fines de semana voy al monte."),

            # Repaso
            ("es", "Repasemos ocio y deportes."),
            ("eu", "Futbola, saskibaloia, igeria, irakurtzea, bidaiatzea."),
            ("es", "Futbol, baloncesto, natacion, leer, viajar."),
            ("es", "Excelente! Has aprendido ocio y deportes. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    11: {
        "title": "Erosketak",
        "title_es": "Las compras",
        "segments": [
            ("eu", "Kaixo! Ongi etorri hamaikagarren ikasgaira."),
            ("es", "Hola, bienvenido a la leccion once. Hoy aprenderemos a hacer compras en euskera."),

            # Tiendas
            ("es", "Tipos de tiendas."),
            ("eu", "Dendak."),
            ("eu", "Supermerkatua."),
            ("es", "Supermercado."),
            ("eu", "Okindegi."),
            ("es", "Okindegi significa panaderia."),
            ("eu", "Harategia."),
            ("es", "Harategia significa carniceria."),
            ("eu", "Arrandegi."),
            ("es", "Arrandegi significa pescaderia."),
            ("eu", "Frutadenda."),
            ("es", "Fruteria."),
            ("eu", "Farmazia."),
            ("es", "Farmacia."),
            ("eu", "Liburudenda."),
            ("es", "Liburudenda significa libreria."),
            ("eu", "Arropa denda."),
            ("es", "Tienda de ropa."),

            # Ropa
            ("es", "La ropa."),
            ("eu", "Arropa."),
            ("eu", "Kamiseta."),
            ("es", "Camiseta."),
            ("eu", "Prakak."),
            ("es", "Prakak significa pantalones."),
            ("eu", "Gona."),
            ("es", "Gona significa falda."),
            ("eu", "Jaka."),
            ("es", "Jaka significa chaqueta."),
            ("eu", "Zapatak."),
            ("es", "Zapatak significa zapatos."),
            ("eu", "Soinekoa."),
            ("es", "Soinekoa significa vestido."),
            ("eu", "Jertsea."),
            ("es", "Jertsea significa jersey."),

            # Precios
            ("es", "Preguntar precios."),
            ("eu", "Zenbat balio du?"),
            ("es", "Zenbat balio du significa cuanto cuesta."),
            ("eu", "Zenbat da?"),
            ("es", "Zenbat da significa cuanto es."),
            ("eu", "Bost euro balio du."),
            ("es", "Cuesta cinco euros."),
            ("eu", "Garestiegia da."),
            ("es", "Garestiegia da significa es muy caro."),
            ("eu", "Merkea da."),
            ("es", "Merkea da significa es barato."),

            # Dialogos de compra
            ("es", "Dialogos utiles para comprar."),
            ("eu", "Egun on, zer nahi duzu?"),
            ("es", "Buenos dias, que desea."),
            ("eu", "Ogia nahi dut, mesedez."),
            ("es", "Quiero pan, por favor."),
            ("eu", "Beste zerbait?"),
            ("es", "Algo mas."),
            ("eu", "Ez, eskerrik asko. Zenbat da?"),
            ("es", "No, gracias. Cuanto es."),
            ("eu", "Bi euro eta berrogeita bost zentimo."),
            ("es", "Dos euros y cuarenta y cinco centimos."),
            ("eu", "Tori, hemen daukazu."),
            ("es", "Toma, aqui tienes."),

            # Tallas
            ("es", "Tallas."),
            ("eu", "Neurria."),
            ("eu", "Txikia."),
            ("es", "Pequena."),
            ("eu", "Ertaina."),
            ("es", "Mediana."),
            ("eu", "Handia."),
            ("es", "Grande."),
            ("eu", "Neurri hau nahi dut."),
            ("es", "Quiero esta talla."),

            # Repaso
            ("es", "Repasemos las compras."),
            ("eu", "Okindegi, harategia, arropa denda. Zenbat balio du?"),
            ("es", "Panaderia, carniceria, tienda de ropa. Cuanto cuesta."),
            ("es", "Muy bien! Has aprendido a comprar. Gero arte!"),
            ("eu", "Gero arte!"),
        ]
    },

    12: {
        "title": "Errepasoa",
        "title_es": "Repaso general",
        "segments": [
            ("eu", "Kaixo! Ongi etorri hamabigarren eta azken ikasgaira."),
            ("es", "Hola, bienvenido a la leccion doce, la ultima leccion. Hoy haremos un repaso general de todo lo aprendido."),

            # Saludos repaso
            ("es", "Repasemos los saludos."),
            ("eu", "Kaixo! Egun on! Arratsalde on! Gabon! Agur! Gero arte!"),
            ("es", "Hola, buenos dias, buenas tardes, buenas noches, adios, hasta luego."),

            # Presentaciones repaso
            ("es", "Las presentaciones."),
            ("eu", "Ni Ander naiz. Madrilgoa naiz. Ikaslea naiz."),
            ("es", "Soy Ander. Soy de Madrid. Soy estudiante."),
            ("eu", "Nire izena Miren da. Donostiarra naiz. Irakaslea naiz."),
            ("es", "Mi nombre es Miren. Soy de San Sebastian. Soy profesora."),

            # Familia repaso
            ("es", "La familia."),
            ("eu", "Aita, ama, anaia, arreba, aitona, amona."),
            ("es", "Padre, madre, hermano, hermana, abuelo, abuela."),
            ("eu", "Nire familiak lau kide ditu."),
            ("es", "Mi familia tiene cuatro miembros."),

            # Numeros repaso
            ("es", "Los numeros."),
            ("eu", "Bat, bi, hiru, lau, bost, sei, zazpi, zortzi, bederatzi, hamar."),
            ("eu", "Hamaika, hamabi, hamahiru, hamalau, hamabost."),
            ("eu", "Hogei, hogeita hamar, berrogei, berrogeita hamar, hirurogei."),
            ("eu", "Hirurogeita hamar, laurogei, laurogeita hamar, ehun."),

            # Colores repaso
            ("es", "Los colores."),
            ("eu", "Gorria, urdina, berdea, horia, zuria, beltza, laranja, morea."),
            ("es", "Rojo, azul, verde, amarillo, blanco, negro, naranja, morado."),

            # Cuerpo repaso
            ("es", "El cuerpo."),
            ("eu", "Burua, begiak, sudurra, ahoa, belarriak, eskuak, hankak."),
            ("es", "Cabeza, ojos, nariz, boca, orejas, manos, piernas."),

            # Comida repaso
            ("es", "La comida."),
            ("eu", "Ogia, ura, kafea, esnea, arrautza, sagarra, haragia, arraina."),
            ("es", "Pan, agua, cafe, leche, huevo, manzana, carne, pescado."),
            ("eu", "Gose naiz. Egarri naiz. Oso goxoa!"),
            ("es", "Tengo hambre. Tengo sed. Muy rico."),

            # Casa repaso
            ("es", "La casa."),
            ("eu", "Egongela, sukaldea, logela, komuna, jangela."),
            ("es", "Salon, cocina, dormitorio, bano, comedor."),
            ("eu", "Ohea, mahaia, aulkia, sofa, armairua."),
            ("es", "Cama, mesa, silla, sofa, armario."),

            # Profesiones repaso
            ("es", "Las profesiones."),
            ("eu", "Irakaslea, medikua, erizaina, abokatua, sukaldaria, saltzailea."),
            ("es", "Profesor, medico, enfermero, abogado, cocinero, vendedor."),

            # Ciudad repaso
            ("es", "La ciudad."),
            ("eu", "Kalea, denda, jatetxea, ospitalea, geltokia, parkea."),
            ("es", "Calle, tienda, restaurante, hospital, estacion, parque."),
            ("eu", "Autobusa, trena, autoa, bizikleta."),
            ("es", "Autobus, tren, coche, bicicleta."),

            # Clima repaso
            ("es", "El clima."),
            ("eu", "Udaberria, uda, udazkena, negua."),
            ("es", "Primavera, verano, otono, invierno."),
            ("eu", "Eguzkia, euria, elurra, haizea."),
            ("es", "Sol, lluvia, nieve, viento."),
            ("eu", "Beroa dago. Hotza dago. Euria ari du."),
            ("es", "Hace calor. Hace frio. Esta lloviendo."),

            # Ocio repaso
            ("es", "Ocio y deportes."),
            ("eu", "Futbola, saskibaloia, igeria, korrika."),
            ("es", "Futbol, baloncesto, natacion, correr."),
            ("eu", "Irakurtzea, musika entzutea, bidaiatzea."),
            ("es", "Leer, escuchar musica, viajar."),

            # Compras repaso
            ("es", "Las compras."),
            ("eu", "Zenbat balio du? Garestiegia da. Merkea da."),
            ("es", "Cuanto cuesta. Es muy caro. Es barato."),

            # Verbos importantes
            ("es", "Los verbos mas importantes que has aprendido."),
            ("eu", "Izan: naiz, zara, da, gara, zarete, dira."),
            ("es", "Ser o estar: soy, eres, es, somos, sois, son."),
            ("eu", "Egon: nago, zaude, dago, gaude, zaudete, daude."),
            ("es", "Estar ubicado."),
            ("eu", "Eduki: dut, duzu, du, dugu, duzue, dute."),
            ("es", "Tener."),

            # Despedida
            ("es", "Enhorabuena! Has completado el curso de euskera nivel A uno."),
            ("es", "Has aprendido saludos, presentaciones, familia, numeros, colores, el cuerpo, comida, la casa, profesiones, la ciudad, el clima, deportes y compras."),
            ("es", "Ahora puedes mantener conversaciones basicas en euskera."),
            ("es", "Sigue practicando y recuerda: el euskera se aprende hablando."),
            ("eu", "Zorionak! Oso ondo egin duzu!"),
            ("es", "Felicidades! Lo has hecho muy bien!"),
            ("eu", "Eskerrik asko eta agur! Gero arte!"),
            ("es", "Muchas gracias y adios! Hasta luego!"),
        ]
    },
}


# ============================================================================
# FUNCIONES DE GENERACION DE AUDIO
# ============================================================================

async def generate_audio_segment(
    text: str,
    voice: str,
    output_path: str,
    rate: str = RATE_ADJUSTMENT
) -> bool:
    """
    Genera un segmento de audio usando edge-tts.

    Args:
        text: Texto a convertir en audio
        voice: Voz de edge-tts a usar
        output_path: Ruta donde guardar el archivo MP3
        rate: Ajuste de velocidad (ej: "-5%", "+10%")

    Returns:
        True si se genero correctamente, False en caso contrario
    """
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Error generando audio: {e}")
        return False


def combine_audio_segments(
    segment_files: List[str],
    output_path: str,
    pause_duration_ms: int = 500
) -> bool:
    """
    Combina multiples archivos de audio en uno solo.

    Args:
        segment_files: Lista de rutas a archivos de audio
        output_path: Ruta donde guardar el archivo combinado
        pause_duration_ms: Duracion de la pausa entre segmentos en milisegundos

    Returns:
        True si se combino correctamente, False en caso contrario
    """
    try:
        # Crear un segmento de silencio para pausas
        pause = AudioSegment.silent(duration=pause_duration_ms)

        # Combinar todos los segmentos
        combined = AudioSegment.empty()
        for i, segment_file in enumerate(segment_files):
            segment = AudioSegment.from_mp3(segment_file)
            combined += segment
            # Anadir pausa entre segmentos (excepto despues del ultimo)
            if i < len(segment_files) - 1:
                combined += pause

        # Exportar el archivo combinado
        combined.export(output_path, format="mp3")
        return True
    except Exception as e:
        print(f"Error combinando audio: {e}")
        return False


async def generate_lesson_podcast(
    lesson_num: int,
    output_dir: Path,
    verbose: bool = True
) -> Optional[str]:
    """
    Genera el podcast completo para una leccion.

    Args:
        lesson_num: Numero de la leccion (1-12)
        output_dir: Directorio donde guardar el podcast
        verbose: Si mostrar mensajes de progreso

    Returns:
        Ruta al archivo generado o None si hubo error
    """
    if lesson_num not in LESSON_SCRIPTS:
        print(f"Error: Leccion {lesson_num} no encontrada.")
        return None

    lesson = LESSON_SCRIPTS[lesson_num]
    segments = lesson["segments"]
    title = lesson["title"]
    title_es = lesson["title_es"]

    if verbose:
        print(f"\n{'='*60}")
        print(f"Generando podcast: Leccion {lesson_num} - {title}")
        print(f"({title_es})")
        print(f"{'='*60}")

    # Crear directorio temporal para segmentos
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        segment_files = []

        # Generar cada segmento
        if HAS_TQDM and verbose:
            iterator = tqdm(enumerate(segments), total=len(segments), desc="Segmentos")
        else:
            iterator = enumerate(segments)

        for i, (lang, text) in iterator:
            # Seleccionar voz segun idioma
            voice = VOICE_EUSKERA if lang == "eu" else VOICE_SPANISH

            # Generar archivo temporal
            segment_file = temp_path / f"segment_{i:04d}.mp3"

            if verbose and not HAS_TQDM:
                print(f"  [{i+1}/{len(segments)}] {lang.upper()}: {text[:50]}...")

            success = await generate_audio_segment(
                text=text,
                voice=voice,
                output_path=str(segment_file)
            )

            if not success:
                print(f"Error en segmento {i}: {text[:30]}...")
                continue

            segment_files.append(str(segment_file))

        if not segment_files:
            print("Error: No se generaron segmentos de audio.")
            return None

        # Asegurar que el directorio de salida existe
        output_dir.mkdir(parents=True, exist_ok=True)

        # Combinar segmentos
        output_file = output_dir / f"lesson-{lesson_num}.mp3"

        if verbose:
            print(f"\nCombinando {len(segment_files)} segmentos...")

        success = combine_audio_segments(
            segment_files=segment_files,
            output_path=str(output_file),
            pause_duration_ms=600  # Pausa de 600ms entre segmentos
        )

        if success:
            if verbose:
                print(f"Podcast guardado en: {output_file}")
            return str(output_file)
        else:
            print("Error al combinar los segmentos de audio.")
            return None


async def generate_all_podcasts(
    output_dir: Path,
    verbose: bool = True
) -> List[str]:
    """
    Genera los podcasts para todas las lecciones.

    Args:
        output_dir: Directorio donde guardar los podcasts
        verbose: Si mostrar mensajes de progreso

    Returns:
        Lista de rutas a los archivos generados
    """
    generated_files = []

    for lesson_num in sorted(LESSON_SCRIPTS.keys()):
        result = await generate_lesson_podcast(lesson_num, output_dir, verbose)
        if result:
            generated_files.append(result)

    return generated_files


def list_lessons():
    """Muestra la lista de lecciones disponibles."""
    print("\nLecciones disponibles:")
    print("-" * 50)
    for num, lesson in sorted(LESSON_SCRIPTS.items()):
        segments_count = len(lesson["segments"])
        print(f"  {num:2d}. {lesson['title']:<25} ({lesson['title_es']})")
        print(f"      {segments_count} segmentos de audio")
    print("-" * 50)
    print(f"Total: {len(LESSON_SCRIPTS)} lecciones")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Funcion principal del script."""
    parser = argparse.ArgumentParser(
        description="Generador de podcasts para el curso de Euskera A1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python generate_podcast.py --lesson 1      # Genera podcast de leccion 1
  python generate_podcast.py --all           # Genera todos los podcasts
  python generate_podcast.py --list          # Lista lecciones disponibles
  python generate_podcast.py -l 1 -v         # Leccion 1 con modo verbose
  python generate_podcast.py -l 1 -o ./mis_podcasts  # Directorio personalizado
        """
    )

    parser.add_argument(
        "-l", "--lesson",
        type=int,
        choices=range(1, 13),
        metavar="N",
        help="Numero de leccion a generar (1-12)"
    )

    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Genera podcasts para todas las lecciones"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista las lecciones disponibles"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=str(PODCASTS_DIR),
        help=f"Directorio de salida (default: {PODCASTS_DIR})"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=True,
        help="Modo verbose (activado por defecto)"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Modo silencioso (desactiva verbose)"
    )

    args = parser.parse_args()

    # Determinar modo verbose
    verbose = args.verbose and not args.quiet

    # Listar lecciones
    if args.list:
        list_lessons()
        return

    # Verificar que se especifico una opcion
    if not args.lesson and not args.all:
        parser.print_help()
        print("\nError: Debes especificar --lesson N o --all")
        sys.exit(1)

    # Directorio de salida
    output_dir = Path(args.output)

    # Ejecutar generacion
    if args.all:
        if verbose:
            print(f"\nGenerando todos los podcasts en: {output_dir}")
        results = asyncio.run(generate_all_podcasts(output_dir, verbose))
        if verbose:
            print(f"\n{'='*60}")
            print(f"Generacion completada!")
            print(f"Podcasts generados: {len(results)}/{len(LESSON_SCRIPTS)}")
            print(f"Ubicacion: {output_dir}")
            print(f"{'='*60}")
    else:
        result = asyncio.run(generate_lesson_podcast(args.lesson, output_dir, verbose))
        if result and verbose:
            print(f"\nGeneracion completada: {result}")


if __name__ == "__main__":
    main()
