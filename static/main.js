document.addEventListener('DOMContentLoaded', () => {

  const randomImages = [
    'random_images/random_1.jpg',
    'random_images/random_2.jpg',
    'random_images/random_3.jpg',
    'random_images/random_4.jpg',
    'random_images/random_5.jpg'
  ];

  const randomIndex = Math.floor(Math.random() * randomImages.length);
  const randomImage = randomImages[randomIndex];

  const heroImageEl = document.getElementById('heroImage');
  if (heroImageEl) {
    heroImageEl.src = randomImage;
  }
});