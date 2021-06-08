class DynamicAllocator:

    def __init__(self, memory_size, holes):
        self.mem_size = memory_size
        self.holes = [hole[:] for hole in holes]
        self.memory = {}
        self.indeces_to_be_dropped = []

    def initalize_memory(self):
        self.merge_holes()
        self.holes.sort()

        if len(self.holes) == 0:
            self.holes.append([0, 0])

        if self.holes[0][0] > 0:
            size = self.holes[0][0]
            self.memory['oldProcess ' + str(1)] = [["", 0, size]]

        for index, hole in enumerate(self.holes):

            start = hole[0] + hole[1]
            size = 0
            if start > self.mem_size or start < 0:
                self.indeces_to_be_dropped.append(index)
                continue

            if index < len(self.holes) - 1:
                size = self.holes[index + 1][0] - start

            if size + start > self.mem_size and self.holes[index + 1][0] + self.holes[index + 1][0] < self.mem_size:
                self.indeces_to_be_dropped.append(index)
                continue

            if size > 0 and size < self.mem_size:
                self.memory['oldProcess ' + str(index + 2)] = [["", start, size]]

        for index in sorted(self.indeces_to_be_dropped, reverse=True):
            del self.holes[index]

        if len(self.indeces_to_be_dropped) > 0:
            self.indeces_to_be_dropped = []
            self.initalize_memory()

        start = self.holes[-1][0] + self.holes[-1][1]
        size = self.mem_size - start
        if size > 0:
            if len(self.holes) > 1:
                self.memory['oldProcess ' + str(len(self.holes) + 1)] = [["", start, size]]
            else:
                self.memory['oldProcess ' + str(len(self.holes))] = [["", start, size]]

        return self.memory

    def remove_process(self, key_to_remove):
        for segment in self.memory[key_to_remove]:
            _, start, size = segment
            self.memory.pop(key_to_remove, None)
            self.holes.append([start, size])

        return 1, self.memory

    def first_fit(self, process_index, segmentations, algo_index):
        self.merge_holes()
        if algo_index == 1:
            self.holes.sort(key=lambda x: x[1])
        elif algo_index == 2:
            self.holes.sort(key=lambda x: x[1], reverse=True)

        size_check = 0
        for segmentation in segmentations:
            for index, hole in enumerate(self.holes):
                if segmentation[1] > hole[1]:
                    size_check = 1

        if size_check == 0:
            self.memory['p' + str(process_index)] = []

            for segmentation in segmentations:
                for index, hole in enumerate(self.holes):
                    if segmentation[1] <= hole[1]:
                        self.memory['p' + str(process_index)].append([segmentation[0], hole[0], segmentation[1]])
                        self.holes[index][1] -= segmentation[1]
                        self.holes[index][0] += segmentation[1]
                        break

        return self.memory, size_check

    def merge_holes(self):
        self.holes.sort(key=lambda x: x[0])
        number_of_holes = len(self.holes)
        index = 1
        while index < number_of_holes:
            if self.holes[index][0] <= self.holes[index-1][0] + self.holes[index-1][1]:
                self.holes[index - 1][1] = (self.holes[index][0] + self.holes[index][1]) - self.holes[index - 1][0]
                self.holes.pop(index)
                number_of_holes -= 1
                index -= 1
            index += 1



    def best_fit(self, process_index, segmentations):
        return self.first_fit(process_index, segmentations, 1)

    def worst_fit(self, process_index, segmentations):
        return self.first_fit(process_index, segmentations, 2)

    def defragmentation(self):
        total_size = 0
        for key in self.memory:
            for process in range(len(self.memory[key])):
                self.memory[key][process][1] = total_size
                total_size += self.memory[key][process][2]
        holes_size = self.mem_size - total_size

        self.holes = [[total_size, holes_size]]

        return self.memory
