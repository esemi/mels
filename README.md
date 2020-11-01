# mels
---

Бегущий город

~8 локаций

~10 команд

список вопросов -  строчки = координаты + картинка + 3 подсказки

вариантов ответа нет

наблюдатели - есть таблица со всеми командами с сортом по выполненным заданиям и времени, которое у них заняло + штрафы

Во время начала игры список задач становится доступен командам.

Команды сами решают, какие задачи в каком порядке делать.

Время старта задачи у всех равно времени начала игры.

Время конца задачи - момент верного ответа на вопрос.

Штрафное время - суммарное на команду и не завязано на таски.



## TODO

### API todo
- ~список игр GET /~
- ~список задач по игре GET /%game_id%/tasks~
- ~читать подсказку GET /%game_id%/tasks/%task_id%/hints/%hint_id%~
- ~ответ на вопрос GET|POST /%game_id%/tasks/%task_id%~
- ~список команд по игре GET /%game_id%/scoring~


### Dummy UI todo
- ~список игр~
- ~список задач по игре html~
- ~ответ на вопрос html~
- ~список команд по игре html~
- ~читать подсказку html~
- ответ на вопрос ajax
- BUG: вывести location.title у таски

### Other
- tests
- deploy
- BUG: double pay by hint view
- BUG: несколько игр одновременно не будут работать в виду пересечения штрафов - можно вынести штрафы отдельно с привязкой к игре
