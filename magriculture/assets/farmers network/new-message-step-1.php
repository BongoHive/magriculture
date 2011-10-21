<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/messages.php">Messages</a> &gt; New Message</div>
		
		<div class="h2">Choose Recipients</div>
		
		<form class="standard" action="/new-message-step-2.php">
			<div class="list overflow">
				<div class="item"><label for="form-group-1">Group name</label> <input type="checkbox" id="form-group-1" /></div>
				<div class="item"><label for="form-group-2">Group name</label> <input type="checkbox" id="form-group-2" /></div>
				<div class="item"><label for="form-group-3">Group name</label> <input type="checkbox" id="form-group-3" /></div>
				<div class="item"><label for="form-group-4">Group name</label> <input type="checkbox" id="form-group-4" /></div>
				<div class="item"><label for="form-group-5">Group name</label> <input type="checkbox" id="form-group-5" /></div>
				<div class="item"><label for="form-group-6">Group name</label> <input type="checkbox" id="form-group-6" /></div>
				<div class="item"><label for="form-group-7">Group name</label> <input type="checkbox" id="form-group-7" /></div>
			</div>
			
			<input type="submit" name="submit" class="submit" value="Next &raquo;" />
			<input type="submit" name="cancel" class="submit" value="cancel" />
			
		</form>		
		
		<div class="h2">Menu</div>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>