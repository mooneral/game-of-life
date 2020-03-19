import pygame
from numpy import genfromtxt
from pygame.locals import *
import numpy as np

class App:

    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    GREY = (220, 220, 220)

    # grid size
    MARGIN = 2
    WIDTH = 18
    HEIGHT = 18

    SPEED = 10

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 800, 800
        self.neighbor_poses = [(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1)]
        self.start = False
        self.space_last = -1

        # main grid
        self.grid = self._make_grid()
        print(f"grid size: {np.shape(self.grid)}")

        # swap grid for updating generation
        self.g_conf = self._make_grid()

        self.clock = pygame.time.Clock()

    def _make_grid(self):
        return np.ones((self.height//(App.HEIGHT + App.MARGIN), self.width//(App.WIDTH + App.MARGIN))) * -1
    
    def _randomized_grid(self):
        self.grid = np.random.choice([1, -1], size=((self.height//(App.HEIGHT + App.MARGIN), self.width//(App.WIDTH + App.MARGIN))), p=[1/5,4/5])
    
    def _reset_grid(self):
        self.grid = self._make_grid()

    def _find_8_nhood(self, pos):
        poss_neighbors = [(pos[0] + i[0], pos[1] + i[1]) for i in self.neighbor_poses]
        neighbors = []
        for i, j in enumerate(poss_neighbors):
            if j[0] >= 0 or j[0] <= np.shape(self.grid)[0] or j[1] >= 0 or j[1] <= np.shape(self.grid)[1]:
                neighbors.append(j)
        return neighbors

    def _apply_rules_neighbors(self, neighbors):

        alive = np.where(self.grid == 1)
        alive_cells = list(zip(alive[0], alive[1]))
        
        # find neighbors of each neighbor
        for n in neighbors:
            nns = self._find_8_nhood(n)

            # remove redundant neighbors
            # nns = list(set(nns).intersection(set(neighbors)))

            counter = 0
            for nn in nns:
                if nn in alive_cells:
                    counter += 1

            # out of scop cells will be removed
            if n[0] > np.shape(self.grid)[0] -1 or n[0] < 0 or n[1] > np.shape(self.grid)[1] -1 or n[1] < 0 :
                pass

            else:# reproduce another cell
                if counter == 3:
                    self.g_conf[n[0]][n[1]] = 1            


    def _apply_rules(self):
        # neighbors = self._find_8_nhood(pos)
        alive = np.where(self.grid == 1)
        alive_cells = list(zip(alive[0], alive[1]))

        for a in alive_cells:
            neighbors = self._find_8_nhood(a)

            # find number of alive cells in 8 neighborhood
            counter = 0
            for n in neighbors:
                if n in alive_cells:
                    counter += 1

            # out of scop cells will be removed
            if a[0] > np.shape(self.grid)[0] -1 or a[0] < 0 or a[1] > np.shape(self.grid)[1] -1 or a[1] < 0 :
                pass

            else:
                # die by isolation
                if counter < 2 and self.grid[a[0]][a[1]] == 1:
                    self.g_conf[a[0]][a[1]]  = -1
                
                # remain alive
                if (counter == 2 or counter == 3)and self.grid[a[0]][a[1]]  == 1:
                    self.g_conf[a[0]][a[1]]  = 1
                
                # die by overcrowding
                if counter > 3 and self.grid[a[0]][a[1]]  == 1:
                    self.g_conf[a[0]][a[1]] = -1

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.size[0], self.size[1]))

        # set the caption for the window
        pygame.display.set_caption("Game of Life")

        # make background white
        self._display_surf.fill(App.WHITE)

        # draw horizontal lines to make the grid
        for row in range(App.HEIGHT, self.width, App.HEIGHT + App.MARGIN):
            pygame.draw.line(self._display_surf, App.GREY, [row,0], [row,self.height], width=2)

        # draw vertical lines to make the grid
        for col in range(App.WIDTH, self.height, App.WIDTH + App.MARGIN):
            pygame.draw.line(self._display_surf, App.GREY, [0,col], [self.width,col], width=2)

        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self._randomized_grid()
            elif event.key == pygame.K_UP:
                self._reset_grid()
            elif event.key == pygame.K_RIGHT:
                np.savetxt(f"patt{np.random.randint(100)}.csv",self.grid, delimiter=',')
            elif event.key == pygame.K_LEFT:
                self.grid = genfromtxt('input.csv', delimiter=',')
            elif event.key == pygame.K_SPACE:
                if self.space_last < 0:
                    self.start = True
                    self.space_last *= -1
                else:
                    self.start = False
                    self.space_last *= -1

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            # Change the x/y screen coordinates to grid coordinates
            col = pos[0] // (App.WIDTH + App.MARGIN)
            row = pos[1] // (App.WIDTH + App.MARGIN)
            # Set that location to one
            
            self.grid[row][col] *= -1
            print("Click ", pos, "Grid coordinates: ", row, col)

    def on_loop(self):
        if self.start:
            self.g_conf = self._make_grid()
            # find alive cells
            ones = np.where(self.grid==1)
            ones= list(zip(ones[0], ones[1]))

            # find neighbors of alive cells
            neighbors = []
            for one in ones:

                # find neighbors
                ns = self._find_8_nhood(one)

                neighbors += ns

            # remove duplicates and alive cells 
            neighbors = list(set(neighbors) - set(ones))

            self._apply_rules_neighbors(neighbors)

            self._apply_rules()

            # update the grid as for a generation
            self.grid = self.g_conf

        ones = np.where(self.grid==1)
        pos_coords= list(zip(ones[0], ones[1]))

        for one in pos_coords:
            x1 = one[1] * (App.WIDTH + App.MARGIN) 
            y1 = one[0] * (App.HEIGHT + App.MARGIN) 
            # x2 = one[0] * (App.WIDTH + App.MARGIN) + (App.WIDTH + App.MARGIN)
            # y2 = one[1] * (App.WIDTH + App.MARGIN) + (App.WIDTH + App.MARGIN)

            pygame.draw.rect(self._display_surf, App.BLACK ,
                [x1, y1, App.WIDTH, App.HEIGHT  ],
                width=0)

        # find dead cells and update cell
        neg_ones = np.where(self.grid==-1)
        neg_coords= list(zip(neg_ones[0], neg_ones[1]))

        # draw white rects as represnt of dead cells
        for neg in neg_coords:
            x1 = neg[1] * (App.WIDTH + App.MARGIN) 
            y1 = neg[0] * (App.HEIGHT + App.MARGIN) 
            # x2 = one[0] * (App.WIDTH + App.MARGIN) + (App.WIDTH + App.MARGIN)
            # y2 = one[1] * (App.WIDTH + App.MARGIN) + (App.WIDTH + App.MARGIN)

            pygame.draw.rect(self._display_surf, App.WHITE ,
                [x1, y1, App.WIDTH, App.HEIGHT  ],
                width=0)

    def on_render(self):
        self.clock.tick(10)
        pygame.display.flip()
  
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()