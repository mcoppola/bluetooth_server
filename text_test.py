import pygame

pygame.init()
window = pygame.display.set_mode((640,480))

while True:
	font = pygame.font.Font(None, 30)
	acc = font.render("accuracy", 1, (255,255,0))
	window.blit(acc, [100,100])
	pygame.display.flip()

pygame.quit()