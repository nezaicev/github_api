 Скрипт выполняет запросы к api.github.com.
Выводит активных участников, пуллреквысты и ошибки.     
Параметры:   
  --u - URL - репозитория который необходимо проанализировать   
    Пример : --u https://github.com/django/django  
  --s - дата начала периода  
  --e - дата конца периода  
    Формат ГГГГ-ММ-ДД.  
    Если пропустить указание данных параметров, анализ будет произведен на неограниченном промежутке времени.  
    Пример : --s 2020-04-14  
  --b  - ветка репозирория, по умолчанию - master  
      --b master  
      
  main.py --u https://github.com/django/django --s 2019-04-14 --e 2020-04-14 --b master  
  
 В качестве варианта реализации CI/CD для подобного сервиса, можно предложит GitHub Actions.
 Данное решение позволяет осуществлять:
    непрерывную интеграцию (создание, тестирование и развертывание ПО);
    оповещения по электронной почте или SMS;
    и т. д.
