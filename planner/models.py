from django.contrib.auth import get_user_model
from django.db import models


class DietTypeChoices(models.TextChoices):
    CLASSIC = 'classic', 'Классическая'
    LOW_CARB = 'low_carb', 'Низкоуглеводная'
    VEGETARIAN = 'vegetarian', 'Вегетарианская'
    KETO = 'keto', 'Кето'


class MealTypeChoices(models.TextChoices):
    BREAKFAST = 'breakfast', 'Завтраки'
    LUNCH = 'lunch', 'Обеды'
    DINNER = 'dinner', 'Ужины'
    DESSERT = 'dessert', 'Десерты'


class Allergy(models.Model):
    name = models.CharField(
        'Аллергия',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Аллергия'
        verbose_name_plural = 'Аллергии'

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):
    DURATION_CHOICES = (
        (1, '1 месяц'),
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
    )
    duration = models.IntegerField(
        'Срок подписки',
        choices=DURATION_CHOICES,
        default=1,
        unique=True,
        db_index=True,
    )
    breakfast_price = models.DecimalField(
        'Цена подписки на завтраки',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    lunch_price = models.DecimalField(
        'Цена подписки на обеды',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    dinner_price = models.DecimalField(
        'Цена подписки на ужины',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    dessert_price = models.DecimalField(
        'Цена подписки на десерты',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = 'Тарифный план'
        verbose_name_plural = 'Тарифные планы'

    def __str__(self) -> str:
        return f"{self.get_duration_display()} "

    def get_price_by_meal_type(self, meal_type: MealTypeChoices):
        prices = {
            MealTypeChoices.BREAKFAST: self.breakfast_price,
            MealTypeChoices.LUNCH: self.lunch_price,
            MealTypeChoices.DINNER: self.dinner_price,
            MealTypeChoices.DESSERT: self.dessert_price,
        }
        return prices.get(meal_type, 0)

    def total_price(self, selected_meal_types: list[MealTypeChoices]):
        total = 0
        for meal_type in selected_meal_types:
            total += self.get_price_by_meal_type(meal_type)
        return total


class UserProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='profile',
    )
    diet_type = models.CharField(
        'Тип диеты',
        choices=DietTypeChoices,
        null=True,
        blank=True,
        db_index=True,
    )
    allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name='Аллергии',
    )
    budget_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ограничение по стоимости',
    )
    persons_count = models.IntegerField(
        default=1,
        verbose_name='Количество персон',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        verbose_name='Тарифный план',
    )
    subscription_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата окончания подписки',
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.user.username


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'Граммы'),
        ('ml', 'Миллилитры'),
        ('pcs', 'Штуки'),
        ('tbsp', 'Столовые ложки'),
        ('tsp', 'Чайные ложки'),
    ]
    name = models.CharField(max_length=150, verbose_name='Название ингредиента')
    allergens = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name='Аллергены',
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Стоимость за единицу',
    )
    callories = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Калорийность',
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='g',
        verbose_name='Единица измерения',
    )

    def __str__(self):
        return f'{self.name} ({self.get_unit_display()})'


class Dish(models.Model):
    DISH_CATEGORY_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('dessert', 'Десерт'),
    ]
    name = models.CharField(max_length=150, verbose_name='Название блюда')
    description = models.TextField(verbose_name='Описание блюда')
    recipe = models.TextField(verbose_name='Рецепт приготовления', blank=True, default='')
    photo = models.ImageField(verbose_name='Фото блюда', blank=True, null=True, upload_to='dishes/')
    diet_type = models.CharField(
        'Тип меню',
        choices=DietTypeChoices,
        null=True,
        blank=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='DishIngredient',
        verbose_name='Ингредиенты',
    )
    category = models.CharField(
        max_length=50,
        choices=DISH_CATEGORY_CHOICES,
        verbose_name='Категория блюда',
        default='lunch',
    )

    @property
    def total_price(self):
        """Считаем общую стоимость блюда"""
        return sum(
            di.quantity * di.ingredient.price
            for di in self.dishingredient_set.all()
        )

    @property
    def total_calories(self):
        return sum(
            di.quantity * di.ingredient.callories
            for di in self.dishingredient_set.all()
        )

    def __str__(self):
        return self.name


class DishIngredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Количество',
    )

    def __str__(self):
        return f'{self.ingredient} - {self.quantity}'
