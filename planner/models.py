from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class DietTypeChoices(models.TextChoices):
    CLASSIC = 'classic', 'Классическое'
    LOW_CARB = 'low_carb', 'Низкоуглеводное'
    VEGETARIAN = 'vegetarian', 'Вегетарианское'
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
        default=0,
    )
    lunch_price = models.DecimalField(
        'Цена подписки на обеды',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    dinner_price = models.DecimalField(
        'Цена подписки на ужины',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    dessert_price = models.DecimalField(
        'Цена подписки на десерты',
        max_digits=10,
        decimal_places=2,
        default=0,
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


class UserSubscription(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscription',
    )
    diet_type = models.CharField(
        'Тип диеты',
        choices=DietTypeChoices.choices,
        db_index=True,
    )
    allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name='Аллергии',
    )
    selected_meal_types = models.JSONField(
        'Выбранные приёмы пищи',
        default=list,
    )
    persons_count = models.IntegerField(
        'Количество персон',
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=1,
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.RESTRICT,
        verbose_name='Тарифный план',
    )
    start_date = models.DateField(
        'Дата начала подписки',
        auto_now_add=True,
    )
    end_date = models.DateField(
        'Дата окончания подписки',
    )

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'

    def __str__(self):
        return f"Подписка {self.user.username}"

    @property
    def is_active(self):
        return self.end_date >= timezone.now().date()

    @property
    def total_price(self):
        return self.plan.total_price(self.selected_meal_types) * self.persons_count


class UserProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='profile',
    )
    budget_limit = models.DecimalField(
        'Ограничение по стоимости',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    avatar = models.ImageField(
        'Аватар',
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
        'Стоимость за единицу',
        max_digits=10,
        decimal_places=2,
    )
    calories = models.DecimalField(
        'Калорийность',
        max_digits=7,
        decimal_places=2,
    )
    unit = models.CharField(
        'Единица измерения',
        max_length=10,
        choices=UNIT_CHOICES,
        default='g',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name} ({self.get_unit_display()})'


class Dish(models.Model):
    name = models.CharField(
        'Название блюда',
        max_length=150,
    )
    description = models.TextField(
        'Описание блюда',
    )
    recipe = models.TextField(
        'Рецепт приготовления',
        blank=True,
        default='',
    )
    photo = models.ImageField(
        'Фото блюда',
        blank=True,
        null=True,
        upload_to='dishes/',
    )
    diet_type = models.CharField(
        'Тип меню',
        choices=DietTypeChoices,
        null=True,
        blank=True,
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='DishIngredient',
        verbose_name='Ингредиенты',
    )
    category = models.CharField(
        'Категория блюда',
        max_length=50,
        choices=MealTypeChoices.choices,
        default=MealTypeChoices.LUNCH,
        db_index=True,
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
            di.quantity * di.ingredient.calories
            for di in self.dishingredient_set.all()
        )

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self):
        return self.name


class DishIngredient(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    quantity = models.DecimalField(
        'Количество',
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Ингридиент блюда'
        verbose_name_plural = 'Ингридиенты блюд'

    def __str__(self):
        return f'{self.ingredient} - {self.quantity}'
