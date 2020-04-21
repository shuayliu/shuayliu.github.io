---
layout: post
title:  "An Ionic Liquid Query Tool"
date:   2020-04-21
excerpt: "ILQuery, one of Jonah Liu's academic tool kits"
tag:
- softerware 
- Academic
---

Here introduce an ionic liquid query tool, one of Jonah Liu's academic tool kits.

I wrote it by C++ with Qt5 library. As the Qt5 EUAL required, the source codes are opened and uploaded to GitHub. You can use it/change it freely under LGPLv3.0.

You can find the original codes through ```Mainpage ->(upright)projects ->ILQuery``` or directly from [here](https://github.com/lsforusual/ILquery).

## HOWTO USE

Just open the software -> type the cation abbreviation & inion abbreviation (I **STRONGLY RECOMMEND** selecting the auto completer to finish ion's abbreviation)-> click *query* button.

## TODO

An un-completed API service was established on https://api.jonahliu.ga/. One can use GET method like ```https://api.jonahliu.ga/?s=ILinfo.basic&cid=c01001&aid=a01001``` obtaining a JSON-typed basic information. It is just the same as this software does.

**BUT** the problem is the ```cid``` and ```aid``` are not easy to get through name or abbreviation.

I am bored to solve this in recent time.

## IF YOU ARE AN EXPERT

You can find the original database-```ildb.db``` in the source codes. It is a SQLite3 database, without additional encryption. You can get more detailed data about IL.

Any problem or suggestion while using the software, please do not hesitate to email me. --you can also find the email address at the [mainpage](https://jonahliu.cf).

## More

About [Me](https://jonahliu.cf/cv)

I won't mind if you were generous enough to give some [financial support](https://jonahliu.cf/donate).