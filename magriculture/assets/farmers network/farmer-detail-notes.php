<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; John Richards</div>
		
		<div class="meta">
			<div class="h2">John Richards <span>Stellenbosch</span></div>
			<span class="subtitle">Grapes</span>
		</div> <!-- /.meta -->
		
		<div class="menu">
			<div class="item"><a href="/new-sale.php"><img src="images/icon-calendar.gif" alt="icon-calendar" width="16" height="16" />Register new Sale &raquo;</a></div>
			<div class="item"><a href="/message-farmer.php"><img src="images/icon-message.gif" alt="icon-message" width="16" height="16" />Message Farmer &raquo;</a></div>
			<div class="item"><a href="/add-note.php"><img src="images/icon-write.gif" alt="icon-write" width="16" height="16" />Add Note &raquo;</a></div>
			<div class="item"><a href="/farmer-profile.php"><img src="images/icon-profile.gif" alt="Farmers" width="16" height="16" />View Profile &raquo;</a></div>
		</div>

		<div class="tabs"><a href="/farmer-detail-sales.php">Sales</a> | <a href="/farmer-detail-messages.php">Messages</a> | Notes</div>

		<div class="list">
			<div class="item">
				<span class="text">New Stock Available</span> <a href="#" class="del">[x]</a><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</div>
			<div class="item">
				<span class="text">This is a note that I wrote</span> <a href="#" class="del">[x]</a><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</div>
			<div class="item">
				<span class="text">Another note about this farmer</span> <a href="#" class="del">[x]</a><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</div>
			<div class="item">
				<span class="text">Very interesting note!</span> <a href="#" class="del">[x]</a><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</div>
			<div class="pagination"><a href="">&laquo; Prev</a> | <a href="">Next &raquo;</a></div>
		</div>
		
		<?php include_once('search-include.php'); ?>	
	
		<div class="h2">Menu</div>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>