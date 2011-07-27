<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/messages.php">Messages</a> &gt; New Message</div>
		
		<h2>Choose Recipients</h2>
		
		<form class="standard" action="/new-message-step-2.php">
			<ul class="list overflow">
				<li><label for="form-group-1">Group name</label> <input type="checkbox" id="form-group-1" /></li>
				<li><label for="form-group-2">Group name</label> <input type="checkbox" id="form-group-2" /></li>
				<li><label for="form-group-3">Group name</label> <input type="checkbox" id="form-group-3" /></li>
				<li><label for="form-group-4">Group name</label> <input type="checkbox" id="form-group-4" /></li>
				<li><label for="form-group-5">Group name</label> <input type="checkbox" id="form-group-5" /></li>
				<li><label for="form-group-6">Group name</label> <input type="checkbox" id="form-group-6" /></li>
				<li><label for="form-group-7">Group name</label> <input type="checkbox" id="form-group-7" /></li>
			</ul>
			
			<input type="submit" name="submit" class="submit" value="Next &raquo;" />
			<input type="submit" name="cancel" class="submit" value="cancel" />
			
		</form>		
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>