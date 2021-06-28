def print_numbers(seconds):
	print("Starting task")
	for num in range(seconds):
		print(num, ". Hello World!")
		time.sleep(1)
	print("Task completed")
        