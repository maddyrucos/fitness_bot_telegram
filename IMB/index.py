def count_index(height, weight):

    try:

        body_index = int(int(weight)/((int(height)/100)*(int(height)/100)))

        if body_index >=18 and body_index <= 25:

            imb_message = (f'<b>Ваш индекс - {body_index}</b>.\nВаш вес <u>в норме.</u> Могу подобрать для Вас <i>тренировку</i> и <i>питание</i>!')


        elif body_index <18 and body_index >= 16:

            imb_message = (f'<b>Ваш индекс - {body_index}</b>.\nУ Вас <u>дефицит массы тела.</u> Могу подобрать для Вас <i>тренировку</i> и <i>питание</i>!')


        elif body_index < 16:

            imb_message = (f'<b>Ваш индекс - {body_index}</b>.\nУ Вас <u>значительный дефицит массы тела.</u> Могу подобрать для Вас <i>тренировку</i> и <i>питание</i>')


        elif body_index > 25 and body_index <=30:

            imb_message = (f'<b>Ваш индекс - {body_index}</b>.\nУ Вас лишний вес. Могу подобрать для Вас <i>тренировку</i> и <i>питание</i>')


        else:

            imb_message = (f'<b>Ваш индекс - {body_index}</b>.\nУ Вас ожирение. Могу подобрать для Вас <i>тренировку</i> и <i>питание</i>')


    except ZeroDivisionError:

        body_index = 0
        imb_message = 'Ошибка. Ваш рост не может быть 0.'


    except ValueError:

        body_index = 0
        imb_message = 'Неверный формат, введите рост и вес цифрами!'


    return body_index, imb_message